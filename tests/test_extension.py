import json
import sys
import cv2
import pytest
from pathlib import Path
from PIL import Image

# Add the components folder to sys.path
sys.path.append(str(Path(".").absolute()))
from classes.tools import Tool
from components.media_optimizer import MediaOptimizer

# Register HEIF support for Pillow
import pillow_heif
pillow_heif.register_heif_opener()

# Register AVIF support for Pillow
import pillow_avif

# Configuration
config: str
with open('config.json', 'r') as file:
    config = json.load(file)

tools = Tool(**config['tool'])
media_optimizer = MediaOptimizer(
    ffmpeg=tools.ffmpeg, ffprobe=tools.ffprobe,
    exiftool=tools.exiftool, xmp_config=tools.config.exiftool_config
)


# Test to check if media files can be opened based on their extensions
@pytest.mark.parametrize("path", Path("./tests/data").glob("*"))
def test_data_ext_support(path):
    print("Registered extensions:", Image.registered_extensions())

    if not path.is_file():
        pytest.skip(f"Not a file: {path}")

    media_path = Path(path)
    mime: str = media_optimizer.get_mime_type(media_path)
    print(mime)

    try:
        if mime.startswith("image/"):
            image = Image.open(media_path)
            image.close()
        elif mime.startswith("video/"):
            video = cv2.VideoCapture(str(media_path))
            if not video.isOpened():
                raise ValueError("Cannot open video file")
            video.release()
        else:
            pytest.fail(f"Unsupported file: {media_path.name}, mimetype: {mime}")
    except Exception:
        pytest.fail(f"Failed: {media_path.name}")