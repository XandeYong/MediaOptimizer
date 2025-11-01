from pydantic import BaseModel
from typing import Optional

class GooglePhotos(BaseModel):
    album_id: Optional[str]