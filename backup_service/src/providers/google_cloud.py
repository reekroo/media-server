from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from .base import BaseProvider
from .. import configs
from .. import backup_logger

log = backup_logger.get_logger(__name__)

class GoogleDriveProvider(BaseProvider):

    def __init__(self):
        self.creds = self._get_credentials()

    def _get_credentials(self) -> Credentials:
        creds = None
        if configs.TOKEN_FILE_PATH.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(configs.TOKEN_FILE_PATH), configs.SCOPES)
            except Exception as e:
                log.warning(f"Failed to load token: {e}. Re-authentication will be required.")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    log.info("Access token has expired. Refreshing...")
                    creds.refresh(Request())
                except Exception as e:
                    log.error(f"Failed to refresh token: {e}. Running full authentication.")
                    creds = self._run_auth_flow()
            else:
                log.info("Token not found or invalid. Running authentication.")
                creds = self._run_auth_flow()

            try:
                with open(configs.TOKEN_FILE_PATH, 'w') as token:
                    token.write(creds.to_json())
                log.info(f"Token saved to file: {configs.TOKEN_FILE_PATH}")
            except Exception as e:
                log.error(f"Failed to save token: {e}")
        
        return creds

    def _run_auth_flow(self) -> Credentials:
        if not configs.CREDENTIALS_FILE_PATH.exists():
            log.critical(f"credentials.json file not found at: {configs.CREDENTIALS_FILE_PATH}")
            log.critical("Please download it from Google Cloud Console and place it in the project root.")
            raise FileNotFoundError("credentials.json not found.")

        flow = InstalledAppFlow.from_client_secrets_file(
            str(configs.CREDENTIALS_FILE_PATH), configs.SCOPES
        )
        
        creds = flow.run_console()
        return creds

    def upload(self, file_path: Path) -> None:
        if not file_path.exists():
            log.error(f"File to upload not found: {file_path}")
            raise FileNotFoundError(f"File to upload not found: {file_path}")

        log.info(f"Starting upload of file '{file_path.name}' to Google Drive.")
        
        try:
            service = build('drive', 'v3', credentials=self.creds)

            file_metadata = {
                'name': file_path.name,
                'parents': [configs.GOOGLE_DRIVE_FOLDER_ID]
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
                    log.info(f"Uploaded {int(status.progress() * 100)}%.")

            log.info(f"File '{file_path.name}' uploaded successfully. File ID: {response.get('id')}")

        except HttpError as error:
            log.error(f"An HTTP error occurred while uploading the file: {error}", exc_info=True)
            raise

        except Exception as e:
            log.error(f"An unknown error occurred with the Google Drive API: {e}", exc_info=True)
            raise