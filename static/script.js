document.addEventListener("DOMContentLoaded", () => {
  const lista = document.getElementById("listaOggetti");
  const form = document.getElementById("oggettoForm");
  const stats = document.getElementById("stats");
  const modal = document.getElementById("modal");
  const modalImg = document.getElementById("modal-img");

  function caricaOggetti() {
    fetch("/oggetti")
      .then(res => res.json())
      .then(dati => {
        lista.innerHTML = "";
        stats.innerHTML = `📊 Totale oggetti trovati: <strong>${dati.length}</strong>`;

        dati.forEach(o => {
          const div = document.createElement("div");
          div.className = "bg-white p-4 rounded shadow relative";

          div.innerHTML = `
            <h3 class="text-lg font-semibold">${o.id} – ${o.sede}</h3>
            <p class="text-gray-700">${o.descrizione}</p>
            <p class="text-sm text-gray-500">${o.luogo}</p>
            <p class="text-sm">Notificato: <strong>${o.notificato}</strong></p>
            <p class="text-xs text-gray-400">${o.data}</p>
            <div class="absolute top-2 right-2 flex gap-2">
              <button onclick="modificaOggetto('${o.id}')" class="text-blue-600 hover:text-blue-800">✏️</button>
              <button onclick="eliminaOggetto('${o.id}')" class="text-red-600 hover:text-red-800">🗑️</button>
            </div>
            ${o.foto ? `
              <div class="mt-3">
                <img src="/static/uploads/${o.foto}" alt="Foto" class="h-16 w-16 object-cover rounded cursor-pointer hover:scale-105 transition"
                  onclick="apriModal('/static/uploads/${o.foto}')">
              </div>` : ''}
          `;
          lista.appendChild(div);
        });
      });
  }

  form.addEventListener("submit", e => {
    e.preventDefault();

    const formData = new FormData(form);

    fetch("/oggetti", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(() => {
      form.reset();
      caricaOggetti();
    });
  });

  window.eliminaOggetto = function(id) {
    if (!confirm("Sei sicuro di voler eliminare questo oggetto?")) return;
    fetch(`/oggetti/${id}`, { method: "DELETE" })
      .then(res => {
        if (res.ok) caricaOggetti();
        else alert("Errore eliminazione");
      });
  }

  window.modificaOggetto = function(id) {
    const nuovaDesc = prompt("Nuova descrizione:");
    const nuovoLuogo = prompt("Nuovo luogo:");
    const nuovoNotif = prompt("Notificato? (sì/no):");

    if (nuovaDesc && nuovoLuogo) {
      fetch(`/oggetti/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          descrizione: nuovaDesc,
          luogo: nuovoLuogo,
          notificato: nuovoNotif || "no"
        })
      })
      .then(res => res.json())
      .then(() => caricaOggetti());
    }
  }

  window.apriModal = function(imgSrc) {
    modalImg.src = imgSrc;
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  };

  modal.addEventListener("click", () => {
    modal.classList.remove("flex");
    modal.classList.add("hidden");
    modalImg.src = "";
  });

  caricaOggetti();
});
