from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os, csv, uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
DATA_FOLDER = "data"
CSV_FILE = os.path.join(DATA_FOLDER, "oggetti.csv")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

def carica_oggetti():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def salva_oggetti(oggetti):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "descrizione", "luogo", "data_ora", "ritrovato_da", "operatore",
            "ufficio", "notificato", "ritirato", "note", "path_foto",
            "data_inserimento", "data_archiviazione"
        ])
        writer.writeheader()
        writer.writerows(oggetti)
    try:
        from drive_utils import backup_data
        backup_data()
    except Exception as e:
        print(f"Drive backup error: {e}")

def genera_id(ufficio, oggetti):
    numero = sum(1 for o in oggetti if o["ufficio"] == ufficio)
    return f"{ufficio}{str(numero + 1).zfill(3)}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        descrizione = request.form["descrizione"]
        luogo = request.form["luogo"]
        data_ora = request.form["data_ora"]
        ritrovato_da = request.form.get("ritrovato_da", "")
        operatore = request.form["operatore"]
        ufficio = request.form["ufficio"]
        notificato = request.form["notificato"]
        ritirato = request.form["ritirato"]
        note = request.form.get("note", "")
        data_inserimento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        giorni = 30 if notificato == "sì" else 90
        data_archiviazione = (datetime.now() + timedelta(days=giorni)).strftime("%Y-%m-%d")

        foto = request.files.get("foto")
        path_foto = ""
        if foto and foto.filename != "":
            filename = secure_filename(f"{uuid.uuid4().hex}_{foto.filename}")
            foto.save(os.path.join(UPLOAD_FOLDER, filename))
            path_foto = os.path.join("static/uploads", filename)

        oggetti = carica_oggetti()
        numero = sum(1 for o in oggetti if o["ufficio"] == ufficio)
        codice_id = f"{ufficio}{str(numero+1).zfill(3)}"

        nuovo_oggetto = {
            "id": codice_id,
            "descrizione": descrizione,
            "luogo": luogo,
            "data_ora": data_ora,
            "ritrovato_da": ritrovato_da,
            "operatore": operatore,
            "ufficio": ufficio,
            "notificato": notificato,
            "ritirato": ritirato,
            "note": note,
            "path_foto": path_foto,
            "data_inserimento": data_inserimento,
            "data_archiviazione": data_archiviazione
        }

        oggetti.append(nuovo_oggetto)
        salva_oggetti(oggetti)
        return redirect("/dashboard")

    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    pwd = request.args.get("pwd", "")
    oggi = datetime.now()

    if not os.path.exists(CSV_FILE):
        oggetti = []
    else:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            oggetti = [
                row for row in reader
                if row["ritirato"] != "sì" and oggi < datetime.strptime(row["data_archiviazione"], "%Y-%m-%d")
            ]

    return render_template("dashboard.html", oggetti=oggetti, admin=(pwd == ADMIN_PASSWORD))

@app.route("/archivio")
def archivio():
    pwd = request.args.get("pwd", "")
    if pwd != ADMIN_PASSWORD:
        return "Accesso negato."
    oggi = datetime.now()
    oggetti = [
        o for o in carica_oggetti()
        if o["ritirato"] == "sì" or oggi >= datetime.strptime(o["data_archiviazione"], "%Y-%m-%d")
    ]
    return render_template("archivio.html", oggetti=oggetti)

@app.route("/archivia/<id>")
def archivia(id):
    pwd = request.args.get("pwd", "")
    if pwd != ADMIN_PASSWORD:
        return "Accesso negato."

    oggetti = carica_oggetti()
    for o in oggetti:
        if o["id"] == id:
            o["ritirato"] = "sì"
    salva_oggetti(oggetti)
    return redirect(url_for("dashboard", pwd=pwd))

@app.route("/modifica/<id>", methods=["GET", "POST"])
def modifica(id):
    oggetti = carica_oggetti()
    trovato = next((o for o in oggetti if o["id"] == id), None)

    if not trovato:
        return "Oggetto non trovato", 404

    if request.method == "POST":
        trovato["descrizione"] = request.form["descrizione"]
        trovato["luogo"] = request.form["luogo"]
        trovato["data_ora"] = request.form["data_ora"]
        trovato["ritrovato_da"] = request.form.get("ritrovato_da", "")
        trovato["operatore"] = request.form["operatore"]
        trovato["ufficio"] = request.form["ufficio"]
        trovato["notificato"] = request.form["notificato"]
        trovato["ritirato"] = request.form["ritirato"]
        trovato["note"] = request.form.get("note", "")
        giorni = 30 if trovato["notificato"] == "sì" else 90
        trovato["data_archiviazione"] = (datetime.now() + timedelta(days=giorni)).strftime("%Y-%m-%d")

        foto = request.files.get("foto")
        if foto and foto.filename:
            filename = secure_filename(f"{uuid.uuid4().hex}_{foto.filename}")
            foto.save(os.path.join(UPLOAD_FOLDER, filename))
            trovato["path_foto"] = os.path.join("static/uploads", filename)

        salva_oggetti(oggetti)
        return redirect("/dashboard")

    return render_template("modifica.html", oggetto=trovato)

@app.route("/admin/export")
def export():
    pwd = request.args.get("pwd", "")
    if pwd != ADMIN_PASSWORD:
        return "Accesso negato."
    if not os.path.exists(CSV_FILE):
        return "Nessun file CSV disponibile."
    return send_file(CSV_FILE, as_attachment=True)

# REST API
@app.route("/api/items", methods=["GET"])
def api_get_items():
    return jsonify(carica_oggetti())


@app.route("/api/items/<id>", methods=["GET"])
def api_get_item(id):
    oggetti = carica_oggetti()
    item = next((o for o in oggetti if o["id"] == id), None)
    if not item:
        return jsonify({"error": "Not found"}), 404
    return jsonify(item)


@app.route("/api/items", methods=["POST"])
def api_create_item():
    data = request.get_json(force=True)
    oggetti = carica_oggetti()

    descrizione = data.get("descrizione", "")
    luogo = data.get("luogo", "")
    data_ora = data.get("data_ora", "")
    ritrovato_da = data.get("ritrovato_da", "")
    operatore = data.get("operatore", "")
    ufficio = data.get("ufficio", "")
    notificato = data.get("notificato", "no")
    ritirato = data.get("ritirato", "no")
    note = data.get("note", "")
    path_foto = data.get("path_foto", "")

    data_inserimento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    giorni = 30 if notificato == "sì" else 90
    data_archiviazione = (datetime.now() + timedelta(days=giorni)).strftime("%Y-%m-%d")

    codice_id = genera_id(ufficio, oggetti)

    nuovo_oggetto = {
        "id": codice_id,
        "descrizione": descrizione,
        "luogo": luogo,
        "data_ora": data_ora,
        "ritrovato_da": ritrovato_da,
        "operatore": operatore,
        "ufficio": ufficio,
        "notificato": notificato,
        "ritirato": ritirato,
        "note": note,
        "path_foto": path_foto,
        "data_inserimento": data_inserimento,
        "data_archiviazione": data_archiviazione,
    }

    oggetti.append(nuovo_oggetto)
    salva_oggetti(oggetti)
    return jsonify(nuovo_oggetto), 201


@app.route("/api/items/<id>", methods=["PUT"])
def api_update_item(id):
    data = request.get_json(force=True)
    oggetti = carica_oggetti()
    item = next((o for o in oggetti if o["id"] == id), None)
    if not item:
        return jsonify({"error": "Not found"}), 404

    for key in ["descrizione", "luogo", "data_ora", "ritrovato_da", "operatore", "ufficio", "notificato", "ritirato", "note", "path_foto"]:
        if key in data:
            item[key] = data[key]

    if "notificato" in data:
        giorni = 30 if item["notificato"] == "sì" else 90
        item["data_archiviazione"] = (datetime.now() + timedelta(days=giorni)).strftime("%Y-%m-%d")

    salva_oggetti(oggetti)
    return jsonify(item)


@app.route("/api/items/<id>", methods=["DELETE"])
def api_delete_item(id):
    oggetti = carica_oggetti()
    new_items = [o for o in oggetti if o["id"] != id]
    if len(new_items) == len(oggetti):
        return jsonify({"error": "Not found"}), 404
    salva_oggetti(new_items)
    return "", 204

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
