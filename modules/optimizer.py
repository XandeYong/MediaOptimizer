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
from components.file_manager import FileManager
from components.media_optimizer import MediaOptimizer
from components.my_logging import log_message
from helper.timespan_logger import TimeSpanLogger
from helper.extension_helper import ExtensionHelper
from constants.media_mime_types import IMAGE_EXT, VIDEO_EXT
from enum import Enum, auto

# Global Param
user_interrupt = False

# Enum Mode for process
class Mode(Enum):
    NORMAL = auto()
    RETRY = auto()

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
image_out_ext = ExtensionHelper.get_extension_from_codec(image_codec)
video_out_ext = ExtensionHelper.get_extension_from_codec(video_codec)

# Optimize media
def _optimize(input_file: str, output_file: str, media_format: str, multiple_frame: bool):
    if media_format == "image":
        return media_optimizer.optimize_image(input_file, output_file, codec=image_codec, multiple_frame=multiple_frame)
    elif media_format == "video":
        return media_optimizer.optimize_video(input_file, output_file, codec=video_codec)
    else:
        raise TypeError(f"Media Format is not supported: {media_format}.")
    
# Recover metadata
def _metadata_recovery(media: Path, guid: str, output_path: str):
    try:
        media_optimizer.replace_metadata(media.absolute(), output_path.absolute())
    except Exception as e:
        log_message(f"[{guid}] metadata_recovery failed: {e}", path_manager.log)

# Metadata Registration
def _set_metadata(media: Path, guid: str, metadatas: dict[str, str]):
    try:
        print(media.suffix, media.suffix == ".mkv")
        if media.suffix == ".mkv": 
            # due to complicated container structure, exiftool doesn't support modify mkv metadata.
            temp_path = path_manager.temp_media / media.name
            media_optimizer.ffmpeg_set_media_metadata(media, temp_path, metadatas)
            shutil.copy2(temp_path, media)
            _delete_file(temp_path, guid, "temporary_metadata")
        else:
            # Register xmp namespace and modify metadata
            media_optimizer.exiftool_set_media_metadata(media, "mediaoptimizer", metadatas, True) # need create one project.ini to keep some of the info like toolkit, version
    except Exception as e:
        log_message(f"[{guid}] set_metadata failed: {e}", path_manager.log)


# Verify media
def _verify(media_path: Path):
    # Verify media type (Image/Video)
    #mime = magic(mime=True).from_file(str(media_file_path))
    mime: str = magic.from_file(str(media_path), mime=True)
    ext: str = media_path.suffix

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

# Count media frames
def _count_frames(image_path: Path):
    with Image.open(image_path) as img:
        try:
            return img.n_frames
        except AttributeError:
            # If n_frames doesn't exist, assume it's a single-frame image
            return 1

# Generate temp media
def _generate_temp_media(media: Path, mime_type: str):
    temp = str(path_manager.temp_media / media.stem) + ExtensionHelper.get_extension_from_mime(mime_type)
    img = Image.open(media)
    img.save(temp, mime_type.split("/")[1], quality=100)
    temp = Path(temp)
    return temp

# Delete file
def _delete_file(file: Path, guid: str, category: str = "unnecessary"):
    log_message(f"[{guid}] Cleanning {category} file...", path_manager.log)
    delete, message = FileManager.delete_file(file)
    if not delete:
        log_message(f"[{guid}] Failed to delete {category} file. path: [{file}], error: {message}", path_manager.log)
    else:
        log_message(f"[{guid}] Deleted {category} file. path: [{file}].", path_manager.log)

    return delete, message

# Process
def process(media: Path, count: int, mode: Mode):
    global user_interrupt
    success: bool = False
    guid = str(uuid.uuid4())
    timer = TimeSpanLogger()
    try:
        log_message(f"[{guid}] Start processing file: [{count}], media: [{media.name}], path: [{media.absolute()}]", path_manager.log)
        timer.start()

        # Variable
        optimize: bool = True
        reduction_percentage: float = 0.0
        multiple_frame: bool = False

        # Verify media type (Image/Video)
        log_message(f"[{guid}] Verifying media file...", path_manager.log)
        media_format, mime_type, ext = _verify(media)
        log_message(f"[{guid}] format: [{media_format}], mime: [{mime_type}], ext: [{media.suffix}]", path_manager.log)

        # Check Raw
        if media_format == "raw":
            log_message(f"[{guid}] Raw media shouldn't be optimize.", path_manager.log)
            shutil.copy2(media, path_manager.raw_media)
            success = True
            return   # Escape

        # Count Frame
        if (media_format == "image"):
            log_message(f"[{guid}] Counting frames...", path_manager.log)
            frames = _count_frames(media)
            if frames > 1:
                log_message(f"[{guid}] Image have more than 1 frame.", path_manager.log)
                multiple_frame = True

        # Verify reprocessing file
        if not args.allow_reprocess and media_optimizer.read_custom_xmp_tag(media.absolute(), "MediaOptimizer", "Optimizer_Toolkit"):
            raise RecursionError(f"Media have been optimized before.")

        # HEIF handling (tile grid (image collection))
        temp = None
        if mime_type in {"image/heic", "image/heif"}:
            log_message(f"[{guid}] Generating temp file...", path_manager.log)
            temp = _generate_temp_media(media, "image/png")
    
        # Optimize the media file
        log_message(f"[{guid}] Optimizing media...", path_manager.log)
        output_ext = image_out_ext if (media_format == "image") else video_out_ext
        output_path: Path = Path(f"{path_manager.optimized_media}/{media.stem}{output_ext}")
        try:
            _optimize(
                temp.absolute() if temp else media.absolute(), 
                output_path, 
                media_format, 
                multiple_frame
            )
        except Exception as e:
            raise e

        log_message(f"[{guid}] Optimized. output: [{output_path}]", path_manager.log)

        # Recover metadata
        log_message(f"[{guid}] Recover metadata...", path_manager.log)
        _metadata_recovery(media, guid, output_path)

        # Verify proficiency
        log_message(f"[{guid}] Verifying optimization proficiency...", path_manager.log)
        original_size = media.stat().st_size
        optimized_size = output_path.stat().st_size
        reduction_percentage = ((original_size - optimized_size) / original_size) * 100
        if optimized_size > original_size:
            log_message(f"[{guid}] Media shouldn't be optimize any further.", path_manager.log)
            optimize = False

            # remove the generated file
            print(f"prepare to remove output_path: {output_path}")

            # rollback to the previous file
            rollback_media = Path(shutil.copy2(media, path_manager.optimized_media))
            print(f"media: {media}, copied path: {rollback_media}")
            if output_path is not rollback_media:
                _delete_file(output_path, guid, "generated")
                output_path = rollback_media

        # Modify media's metadata
        log_message(f"[{guid}] Altering metadata...", path_manager.log)
        
        # Register xmp namespace and modify metadata
        _set_metadata(output_path, guid, {
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
        })

        log_message(f"[{guid}] Metadata modified.", path_manager.log)
        
        # Clean temp file
        if not args.keep_temp and temp:
            _delete_file(temp, guid, "temporary")

        success = True
    except KeyboardInterrupt as e:
        if not str(e).strip():
            e = "User Interrupted."
        exception_action(media, guid, e, mode)
        user_interrupt = True

    except Exception as e:
        exception_action(media, guid, e, mode)
    finally:
        timer.stop()
        log_message(f"[{guid}] End process. Elapsed: {timer}", path_manager.log)
        return success

# Core exception action
def exception_action(media, guid, e, mode):
    try:
        log_message(f"[{guid}] Error: {e}", path_manager.log)
        log_message(f"[{guid}] Error: {e}", path_manager.failed_log)

        if mode == Mode.NORMAL:
            # copy file to failed_media folder
            shutil.copy2(media, path_manager.failed_media)

        # delete file that are failed during the process in optimized_media folder
        failed_file = Path(path_manager.optimized_media / media.name)
        _delete_file(failed_file, guid, "failed")

    except Exception as err:
        log_message(f"[{guid}] exception_action failed: {err}", path_manager.log)

    
# Batch process
def batch_process(files: list[Path], mode: Mode):
    count: int = 1
    for media in files:
        success = process(media, count, mode)
        count += 1

        if mode == Mode.RETRY and success:
            delete, message = FileManager.delete_file(media)
            if not delete:
                raise Exception(message)



# Optimizer
def process_medias(files: list[Path]):
    log_message(f"Optimizer started", path_manager.log)
    optimizer_timer = TimeSpanLogger()
    optimizer_timer.start()

    batch_process(files, Mode.NORMAL)

    while args.retry_failed and not user_interrupt:
        failed_files, image_count, video_count = FileManager.collect_media_files(path_manager.failed_media, IMAGE_EXT, VIDEO_EXT)
        if failed_files:
            log_message(f"Retry failed files started", path_manager.log)
            log_message(f"Total files: {len(failed_files)}, image: {image_count}, video: {video_count}", path_manager.log)
            batch_process(failed_files, Mode.RETRY)
            log_message(f"Retry failed files ended", path_manager.log)
        else:
            break
    optimizer_timer.stop()
    log_message(f"Optimizer ended. Elapsed: {optimizer_timer}", path_manager.log)

            
        
        

# MAIN (Manual Run)
if __name__ == "__main__":
    process_medias()