import pytest
from pathlib import Path
from magic import magic

UNKNOWN_MIME_TYPE = ["application/octet-stream", "inode/blockdevice"]

@pytest.mark.parametrize("media_path", Path("./tests/data").glob("*"))
def test_magic(media_path: Path):
    try:
        mime: str = magic.from_file(str(media_path), mime=True)
        if mime in UNKNOWN_MIME_TYPE: 
            if media_path.suffix.lower() in ['.heic', '.heif', '.avif']:
                pytest.skip(f"Expected result due to Magic in window can't support it (29-Oct-2025): {media_path.name}, mime: {mime}")
            else:
                pytest.fail(f"Magic returned unknown mime type: {media_path.name}, mime: {mime}")
    except Exception as e:
        pytest.fail(f"Magic failed: {media_path.name}, error: {e}")