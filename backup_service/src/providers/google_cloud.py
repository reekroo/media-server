import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from .base import BaseProvider

class GoogleDriveProvider(BaseProvider):
    def __init__(self, logger: logging.Logger, token_path: Path, creds_path: Path, folder_id: str, scopes: list):
        self.log = logger
        self.token_path = token_path
        self.creds_path = creds_path
        self.folder_id = folder_id
        self.scopes = scopes
        self.creds = self._get_credentials()

    def _get_credentials(self) -> Credentials:
        creds = None
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_path), self.scopes)
            except Exception as e:
                self.log.warning(f"Failed to load token: {e}. Re-authentication will be required.")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    self.log.info("Access token has expired. Refreshing...")
                    creds.refresh(Request())
                except Exception as e:
                    self.log.error(f"Failed to refresh token: {e}. Running full authentication.")
                    creds = self._run_auth_flow()
            else:
                self.log.info("Token not found or invalid. Running authentication.")
                creds = self._run_auth_flow()

            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                self.log.info(f"Token saved to file: {self.token_path}")
            except Exception as e:
                self.log.error(f"Failed to save token: {e}")
        
        return creds

    def _run_auth_flow(self) -> Credentials:
        if not self.creds_path.exists():
            self.log.critical(f"credentials.json file not found at: {self.creds_path}")
            self.log.critical("Please download it from Google Cloud Console and place it in the project root.")
            raise FileNotFoundError("credentials.json not found.")

        flow = InstalledAppFlow.from_client_secrets_file(
            str(self.creds_path), self.scopes
        )
        
        creds = flow.run_console()
        return creds

    def upload(self, file_path: Path) -> None:
        if not file_path.exists():
            self.log.error(f"File to upload not found: {file_path}")
            raise FileNotFoundError(f"File to upload not found: {file_path}")

        self.log.info(f"Starting upload of file '{file_path.name}' to Google Drive.")
        
        try:
            service = build('drive', 'v3', credentials=self.creds)

            file_metadata = {
                'name': file_path.name,
                'parents': [self.folder_id]
            }
            media = MediaFileUpload(str(file_path), mimetype='application/zip', resumable=True)

            request = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    self.log.info(f"Uploaded {int(status.progress() * 100)}%.")

            self.log.info(f"File '{file_path.name}' uploaded successfully. File ID: {response.get('id')}")

        except HttpError as error:
            self.log.error(f"An HTTP error occurred while uploading the file: {error}", exc_info=True)
            raise

        except Exception as e:
            self.log.error(f"An unknown error occurred with the Google Drive API: {e}", exc_info=True)
            raise