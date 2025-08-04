from pydantic import BaseModel

class Config(BaseModel):
    exiftool_config: str

class Tool(BaseModel):
    ffmpeg: str
    ffprobe: str
    exiftool: str
    config: Config