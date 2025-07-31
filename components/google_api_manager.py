import os
import requests
import magic
from pathlib import Path
from http import HTTPStatus
from datetime import datetime
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleAPIManager:
    """
    Manages Google API authentication and media upload/creation.
    Handles OAuth2 credentials, uploads media files to Google servers,
    and creates media items in Google Photos via REST API.

    # Not possible for fetch/download anymore due to (https://issuetracker.google.com/issues/368779600?pli=1)
    """

    def __init__(self, 
        client_secret_file: str,
        token_file: str,
        validate_token_url: str,
        media_upload_url: str, 
        media_create_url: str,
        token_scopes: list[str]
    ):
        """
        Initializes the GoogleAPIManager with authentication and API configuration.

        Args:
            client_secret_file (str): Path to OAuth2 client secret JSON file.
            token_file (str): Path to the token file for saving/loading credentials.
            validate_token_url (str): URL to validate the token.
            media_upload_url (str): API endpoint to upload media.
            media_create_url (str): API endpoint to create media items.
            token_scopes (list[str]): List of OAuth2 scopes required for the token.
        """
                
        self._client_secret_file = client_secret_file
        self._token_file = token_file
        self._validate_token_api = validate_token_url
        self._upload_media_api = media_upload_url
        self._create_media_api = media_create_url
        self._token_scopes = token_scopes
        self._creds: Credentials = self._load_stored_token()

        if not self._creds:
            self._authorize()


    #region Credentials
    # Create or refresh credentials
    def _authorize(self):
        """
        Authorizes the user using OAuth2. Loads from token file if available,
        otherwise starts a local server to get new credentials and saves them.
        """

        # try to get creds
        self._creds = self._load_stored_token()

        # Reset credentials for regenerating a new one due to different scope being given
        if self._creds and sorted(self._creds.scopes) != sorted(self._token_scopes):
            self._creds = None

        # If there are no (valid) credentials, get new ones
        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self._client_secret_file, self._token_scopes)
                self._creds = flow.run_local_server(port=8080, access_type="offline", prompt="consent")

            # Save the credentials for future use
            with open(self._token_file, 'w') as token:
                token.write(self._creds.to_json())

    # Read Credentials from token file
    def _load_stored_token(self):
        """
        Loads stored credentials from the token file.

        Returns:
            Credentials | None: Google credentials if found, otherwise None.
        """

        if os.path.exists(self._token_file):
            return Credentials.from_authorized_user_file(self._token_file)
        return None
        
    # Validate token
    def _is_token_active(self):
        """
        Validates the current token by making a request to the validation URL.

        Returns:
            bool: True if token is valid, False otherwise.
        """

        if self._creds and self._creds.token:
            url = self._validate_token_api.replace("{token}", self._creds.token)
            response = requests.get(url)
            return response.status_code == HTTPStatus.OK
        return False
    
    # Validate and generate or refresh token when necessary
    def _ensure_token_valid(self):
        """
        Ensures the access token is valid, refreshing or reauthorizing if necessary.

        Returns:
            bool: True when token is valid.
        
        Raises:
            ValueError: If token scopes are empty during authorization.
        """

        if not self._is_token_active():
            if self._token_scopes == []:
                raise ValueError("Token scopes must be provided.")
            self._authorize()
        return True
    #endregion

    #region Upload
    def _auth_headers(self, content_type: str = "application/json", extra_headers: dict[str, str] | None = None):
        """
        Builds headers including the authorization token and content type.

        Args:
            content_type (str): The value of Content-Type header. Defaults to "application/json".
            extra_headers (dict[str, str] | None): Optional dictionary of additional headers.

        Returns:
            dict: Complete header dictionary for authenticated requests.
        """

        headers = {
            "Authorization": f"Bearer {self._creds.token}",
            "Content-Type": content_type
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    # Upload media stream to google server
    def upload_media(self, file_path: Path):
        """
        Uploads a media file to Google's upload endpoint and returns the upload token.

        Args:
            file_path (Path): Path to the media file to upload.

        Returns:
            str: The upload token received from Google.

        Raises:
            Exception: On file read errors or if the upload fails.
        """

        # Keep token alive
        self._ensure_token_valid()
        
        file_name = file_path.name
        mime = magic.Magic(mime=True).from_file(str(file_path))

        headers = self._auth_headers(
            content_type = "application/octet-stream",
            extra_headers = {
                "X-Goog-Upload-File-Name": file_name,
                "X-Goog-Upload-Content-Type": mime,
                "X-Goog-Upload-Protocol": "raw",
            }
        )

        try:
            with open(file_path, "rb") as file:
                upload_response = requests.post(self._upload_media_api, headers=headers, data=file)

            if upload_response.status_code != HTTPStatus.OK:
                raise ConnectionError(upload_response.text)

            return upload_response.text.strip() # Upload Token
        except ConnectionError as e:
            raise Exception(f"Upload token request failed for {file_name}: {e}")
        except Exception as e:
            raise Exception(f"Error reading file {file_name}: {e}")


    # Create media file from google server
    def create_media_item(self, upload_token: str, filename: str, album_id: str = None):
        """
        Creates a media item on Google Photos using the given upload token.

        Args:
            upload_token (str): The token received from a successful media upload.
            filename (str): The name of the file for logging/description purposes.
            album_id (str, optional): Optional album ID to associate the media item with.

        Returns:
            str: JSON response from the media item creation request.
        """
        
        # Keep token alive
        self._ensure_token_valid()

        optimized_date = datetime.now(ZoneInfo("Asia/Singapore")).isoformat()
        headers = self._auth_headers()

        # Payload
        payload = {}
        if album_id:
            payload["albumId"] = album_id
        payload["newMediaItems"] = [
            {
                "description": f"[Image: {filename}][Optimized date: {optimized_date}]",
                "simpleMediaItem": {
                    "uploadToken": upload_token
                }
            }
        ]

        response = requests.post(self._create_media_api, headers=headers, json=payload)
        return response.text
    #endregion