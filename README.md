# Lost and Found App

This repository contains a small Flask application used to record found items and manage them through a simple dashboard. Items are stored in `data/oggetti.csv` and associated photos are saved in `static/uploads`.

## Setup

1. Ensure Python 3 is available on your system.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   Additional packages for optional Google Drive backup are listed in `requirements.txt`.

## Running the Application

Run the development server with:
```bash
python app.py
```
The app will listen on port `5000` by default.

## Google Drive Backup

If a `credentials.json` file for a Google API project is present in the project
root, the application will automatically upload `data/oggetti.csv` and any files
under `static/uploads` to your Google Drive each time the data is saved. On the
first run you will be prompted to authorize access, which creates `token.json`
for subsequent executions.

## Admin Password

Some routes (like viewing the archive or exporting data) require an administrator password. The application reads the password from the `ADMIN_PASSWORD` environment variable and falls back to `admin123` if it is not set. Provide the password via the `pwd` query parameter when accessing protected routes.


## Sample Data

The `sample-data` directory holds example files (`oggetti.csv`, `oggetti.json` and `salva_csv`) that demonstrate the data format. They are not used by the application at runtime and are provided for reference only.


## Tests

Install the additional development requirements and run the test suite with:
```bash
pip install -r requirements-dev.txt
pytest
```
The tests simply verify that key routes return HTTP 200 responses.
