from typing import Optional, List
from pydantic import BaseModel

class Argument(BaseModel):
    name: Optional[str] = None
    operation: Optional[int] = None
    source: Optional[str] = None
    image_quality: Optional[int] = None
    video_quality: Optional[int] = None
    image_output_codec: Optional[str] = None
    video_output_codec: Optional[str] = None
    media: Optional[str] = None
    extension: Optional[List[str]] = None
    keep_temp: bool
    allow_reprocess: bool
    retry_failed: bool
