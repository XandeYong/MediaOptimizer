import os
import uuid
import shutil
import cv2
import pillow_heif
from app_info import APP_NAME, VERSION
from magic import magic
from datetime import datetime, UTC
from pathlib import Path
from PIL import Image
from main import container
from classes.path_manager import PathManager
from components.media_optimizer import MediaOptimizer
from components.my_logging import log_message
from helper.timespan_logger import TimeSpanLogger


# Injecting dependency
path_manager: PathManager = container.path_manager
media_optimizer: MediaOptimizer = container.media_optimizer

# Register HEIF support with Pillow
pillow_heif.register_heif_opener()

# file to skip (optimizing raw image is pointless, why take raw image in the first place)
skip = ["image/tiff"]

# Optimize media
def _optimize(input_file: str, output_file: str, media_format: str, mime_type: str = None):
    if media_format == "image":
        return media_optimizer.optimize_to_jpeg(input_file, mime_type, output_file) # need to pass in ext (for HEIC verification)
    elif media_format == "video":
        return media_optimizer.optimize_to_mp4(input_file, output_file)
    else:
        raise TypeError(f"Media Format is not supported: {media_format}.")

# Verify media
def _verify(media_path: Path):
    # Verify media type (Image/Video)
    #mime = magic(mime=True).from_file(str(media_file_path))
    mime: str = magic.from_file(str(media_path), mime=True)

    if mime == "application/octet-stream" or mime == "inode/blockdevice":
        mime = media_optimizer.get_mime_type(media_path)

    for m in skip:
        if mime == m:
            return "raw", mime, os.path.splitext(media_path)[-1]

    if mime.startswith("image"):
        # try image
        try:
            image = Image.open(media_path)
            image.close()
            return "image", mime, os.path.splitext(media_path)[-1]
        except Exception as e:
            raise RuntimeError(e)
    
    elif mime.startswith("video"):
        # try video
        try:
            video = cv2.VideoCapture(str(media_path))
            if not video.isOpened():
                raise ValueError("Cannot open video file")
            video.release()
            return "video", mime, os.path.splitext(media_path)[-1]
        except Exception as e:
            raise RuntimeError(e)

    raise ValueError(f"Unsupported MIME type: [{mime}]")



# Optimizer
def process_medias(files: list[Path]):
    log_message(f"Optimizer started", path_manager.log)
    count: int = 0
    for media in files:
        guid = str(uuid.uuid4())
        timer = TimeSpanLogger()
        try:
            log_message(f"[{guid}] Start processing file: [{count}], media: [{media.name}], path: [{media.absolute()}]", path_manager.log)
            timer.start()

            # Variable
            optimize: bool = True
            reduction_percentage: float = 0.0
            count += 1

            # Verify media type (Image/Video)
            log_message(f"[{guid}] Verifying media file...", path_manager.log)
            media_format, mime_type, ext = _verify(media)
            log_message(f"[{guid}] format: [{media_format}], mime: [{mime_type}], ext: [{os.path.splitext(media)[-1]}]", path_manager.log)

            if media_format == "raw":
                log_message(f"[{guid}] Raw media shouldn't be optimize.", path_manager.log)
                shutil.copy2(media, path_manager.raw_media)
                continue

            # Verify processed?
            google_id: str = media_optimizer.read_custom_xmp_tag(media.absolute(), "MediaOptimizer", "Optimizer_Toolkit")
            if (google_id):
                raise RecursionError(f"Media have been optimized before.")
            google_id = media.name.split(".")[0]

            # Optimize the media
            log_message(f"[{guid}] Optimizing media...", path_manager.log)
            pre_output: str = path_manager.optimized_media / media.name
            output_path = Path(_optimize(media.absolute(), pre_output, media_format, mime_type))
            log_message(f"[{guid}] Optimized. output: [{output_path}]", path_manager.log)

            # Verify proficiency
            original_size = media.stat().st_size
            optimized_size = output_path.stat().st_size
            reduction_percentage = ((original_size - optimized_size) / original_size) * 100
            if optimized_size > original_size:
                log_message(f"[{guid}] Media shouldn't be optimize any further.", path_manager.log)
                optimize = False

                # rollback to the previous file
                if not ext == ".jpeg":
                    output_path = Path(pre_output)
                shutil.copy2(media, output_path)

            # Modify media's metadata
            log_message(f"[{guid}] Altering metadata...", path_manager.log)

            # Register xmp namespace and modify metadata
            media_optimizer.set_media_metadata(output_path, "mediaoptimizer", {
                "Optimizer_Toolkit": str(APP_NAME),
                "Optimizer_Version": str(VERSION),
                "Optimize_Date": str(datetime.now(UTC).isoformat()),
                "Optimize": str(optimize),
                "Optimize_Tool": media_optimizer.get_ffmpeg_version,
                "Input_Format": str(mime_type),
                "Output_Format": str(_verify(output_path)[1]),
                "Original_Size": str(original_size),
                "Optimized_Size": str(optimized_size),
                "Size_Reduction_Percent": str(round(reduction_percentage, 2))
            }, True) # need create one project.ini to keep some of the info like toolkit, version

            log_message(f"[{guid}] Metadata modified.", path_manager.log)
        except Exception as e:
            log_message(f"[{guid}] Error: {e}", path_manager.log)
            log_message(f"[{guid}] Error: {e}", path_manager.failed_log)
            shutil.copy2(media, path_manager.failed_media)
        timer.stop()
        log_message(f"[{guid}] End process. Elapsed: {timer}", path_manager.log)
        

# MAIN (Manual Run)
if __name__ == "__main__":
    process_medias()