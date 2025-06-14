import os
import mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = os.getenv('GDRIVE_CREDENTIALS', 'credentials.json')
TOKEN_FILE = 'token.json'
UPLOAD_FOLDER = 'static/uploads'
CSV_FILE = 'data/oggetti.csv'

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError('Missing credentials.json for Google Drive')
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_file(service, path, parent_id=None):
    file_metadata = {'name': os.path.basename(path)}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    mime_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    media = MediaFileUpload(path, mimetype=mime_type, resumable=True)
    service.files().create(body=file_metadata, media_body=media).execute()

def backup_data():
    if not os.path.exists(CREDENTIALS_FILE):
        print('Google Drive credentials not found; skipping backup.')
        return
    service = get_service()
    if os.path.exists(CSV_FILE):
        upload_file(service, CSV_FILE)
    if os.path.isdir(UPLOAD_FOLDER):
        for fname in os.listdir(UPLOAD_FOLDER):
            path = os.path.join(UPLOAD_FOLDER, fname)
            if os.path.isfile(path):
                upload_file(service, path)
