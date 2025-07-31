from pydantic import BaseModel
from typing import Optional, List


class MediaMetadata(BaseModel):
    creationTime: str
    width: str
    height: str


class MediaItem(BaseModel):
    id: str
    productUrl: str
    mimeType: str
    mediaMetadata: MediaMetadata
    filename: str


class UploadStatus(BaseModel):
    message: str


class NewMediaItemResult(BaseModel):
    uploadToken: str
    status: UploadStatus
    mediaItem: MediaItem


class ErrorResponse(BaseModel):
    code: int
    message: str
    status: str


class GoogleUploadResponse(BaseModel):
    newMediaItemResults: Optional[List[NewMediaItemResult]] = None
    error: Optional[ErrorResponse] = None

    def is_success(self) -> bool:
        return self.newMediaItemResults is not None
