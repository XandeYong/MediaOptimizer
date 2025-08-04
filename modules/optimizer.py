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
from classes.argument import Argument
from classes.path_manager import PathManager
from components.media_optimizer import MediaOptimizer
from components.my_logging import log_message
from helper.timespan_logger import TimeSpanLogger
from constants.media_mime_types import MEDIA_MIME_TYPES


# Injecting dependency
args: Argument = container.args
path_manager: PathManager = container.path_manager
media_optimizer: MediaOptimizer = container.media_optimizer

# Register HEIF support with Pillow
pillow_heif.register_heif_opener()
pillow_heif.register_avif_opener()

# file to skip (optimizing raw image is pointless, why take raw image in the first place)
skip = ["image/tiff"]
image_codec = args.image_output_format or "libaom-av1"
video_codec = args.video_output_format or "libx265"

# Optimize media
def _optimize(input_file: str, output_file: str, media_format: str):
    if media_format == "image":
        return media_optimizer.optimize_image(input_file, output_file, codec=image_codec)
    elif media_format == "video":
        return media_optimizer.optimize_video(input_file, output_file, codec=video_codec)
    else:
        raise TypeError(f"Media Format is not supported: {media_format}.")

# Verify media
def _verify(media_path: Path):
    # Verify media type (Image/Video)
    #mime = magic(mime=True).from_file(str(media_file_path))
    mime: str = magic.from_file(str(media_path), mime=True)
    ext: str = os.path.splitext(media_path)[-1]

    if mime == "application/octet-stream" or mime == "inode/blockdevice":
        mime = media_optimizer.get_mime_type(media_path)

    for m in skip:
        if mime == m:
            return "raw", mime, ext

    if mime.startswith("image"):
        # try image
        try:
            image = Image.open(media_path)
            image.close()
            return "image", mime, ext
        except Exception as e:
            raise RuntimeError(e)
    
    elif mime.startswith("video"):
        # try video
        try:
            video = cv2.VideoCapture(str(media_path))
            if not video.isOpened():
                raise ValueError("Cannot open video file")
            video.release()
            return "video", mime, ext
        except Exception as e:
            raise RuntimeError(e)

    raise ValueError(f"Unsupported MIME type: [{mime}]")

# Generate temp media
def _generate_temp_media(media: str, mime_type: str):
    temp = str(path_manager.temp_media / os.path.splitext(media.name)[0]) + MEDIA_MIME_TYPES[mime_type]
    img = Image.open(media)
    img.save(temp, mime_type.split("/")[1], quality=100)
    temp = Path(temp)
    return temp

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

            # Verify reprocessing file
            if not args.allow_reprocess and media_optimizer.read_custom_xmp_tag(media.absolute(), "MediaOptimizer", "Optimizer_Toolkit"):
                raise RecursionError(f"Media have been optimized before.")

            # HEIF handling (tile grid (image collection))
            temp = None
            if mime_type in {"image/heic", "image/heif"}:
                log_message(f"[{guid}] Generating temp file...", path_manager.log)
                temp = _generate_temp_media(media.absolute(), "image/png")
        
            # Optimize the media
            log_message(f"[{guid}] Optimizing media...", path_manager.log)
            pre_output: str = path_manager.optimized_media / media.name
            output_path = Path(_optimize(temp.absolute() if temp else media.absolute(), pre_output, media_format))
            log_message(f"[{guid}] Optimized. output: [{output_path}]", path_manager.log)

            # Clean temp file
            if not args.keep_temp and temp and temp.exists():
                log_message(f"[{guid}] Cleanning temp file...", path_manager.log)
                temp.unlink()

            # Recover metadata
            log_message(f"[{guid}] Recover metadata...", path_manager.log)
            media_optimizer.replace_metadata(media.absolute(), output_path.absolute())

            # Verify proficiency
            log_message(f"[{guid}] Verifying optimization proficiency...", path_manager.log)
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