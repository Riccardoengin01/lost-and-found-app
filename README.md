# Lost and Found App

This repository contains a small Flask application used to record found items and manage them through a simple dashboard. Items are stored in `data/oggetti.csv` and associated photos are saved in `static/uploads`.

## Setup

1. Ensure Python 3 is available on your system.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   The only dependency is Flask as listed in `requirements.txt`.

## Running the Application

Run the development server with:
```bash
python app.py
```
The app will listen on port `5000` by default.

## Admin Password

Some routes (like viewing the archive or exporting data) require an administrator password. The password is defined in `app.py` as `admin123` and must be provided via the `pwd` query parameter when accessing protected routes.

