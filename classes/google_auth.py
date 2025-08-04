from pydantic import BaseModel
from typing import Optional, List


class Scope(BaseModel):
    appendonly: str

class FilePath(BaseModel):
    client_secret_file: str
    token_file: str

class GoogleAPI(BaseModel):
    validate_token_url: str
    media_upload_url: str
    media_create_url: str

class GoogleAuth(BaseModel):
    scope: Scope
    file_path: FilePath
    google_api: GoogleAPI