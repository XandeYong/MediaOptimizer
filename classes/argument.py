from typing import Optional, List
from pydantic import BaseModel

class Argument(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    image_quality: Optional[int] = None
    video_quality: Optional[int] = None
    image_output_format: Optional[str] = None
    video_output_format: Optional[str] = None
    media: Optional[str] = None
    extension: Optional[List[str]] = None
    keep_temp: bool
    allow_reprocess: bool