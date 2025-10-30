import shutil
import uuid
from classes.argument import Argument
from classes.google_photos import GooglePhotos
from mediaoptimizer import container
from classes.path_manager import PathManager
from components.google_api_manager import GoogleAPIManager
from components.my_logging import log_message
from helper.timespan_logger import TimeSpanLogger
from pathlib import Path

# Injecting dependency
path_manager: PathManager = container.path_manager
google_api_manager: GoogleAPIManager = container.google_api_manager
google_photos: GooglePhotos = container.google_photos
args: Argument = container.args

# Variables
count_success = 0
count_failed = 0

def _move_file(media: Path, dest: Path):
    if args.operation == 2:
        shutil.copy2(media, dest)
    else:
        shutil.move(media, dest)

def _upload_media(media: Path, count: int):
    success: bool = False
    guid = str(uuid.uuid4())
    timer = TimeSpanLogger()
    try:
        log_message(f"[{guid}] Start processing file: [{count}], media: [{media.name}], path: [{media.absolute()}]", path_manager.log)
        timer.start()

        # Upload media to google server and retrieve upload token
        log_message(f"[{guid}] Uploading media file...", path_manager.log)
        upload_token = google_api_manager.upload_media(media)
        log_message(f"[{guid}] upload_token: {upload_token}", path_manager.log)

        # Validate upload token
        if upload_token == "":
            raise Exception("Upload token is empty.")
        
        # Create media item from upload token
        log_message(f"[{guid}] Creating media item...", path_manager.log)
        response = google_api_manager.create_media_item(upload_token, media.name, google_photos.album_id)

        log_message(f"[{guid}] Response: {response.json()}", path_manager.log)
        
        # Move file to uploaded folder
        log_message(f"[{guid}] Moving media file...", path_manager.log)
        _move_file(media, path_manager.uploaded_media)
        
        success = True
        log_message(f"[{guid}] Successfully uploaded media: {media.name}.", path_manager.log)

    except Exception as e:
        log_message(f"[{guid}] Error: {e}", path_manager.log)
        _move_file(media, path_manager.failed_upload_media)
    finally:
        timer.stop()
        log_message(f"[{guid}] End process. Elapsed: {timer}", path_manager.log)
        return success

def upload_all_medias(media_files: list[Path]):
    count: int = 1
    count_failed = 0
    try:
        log_message("Upload process started - Google Photos", path_manager.log)
        uploader_timer = TimeSpanLogger()
        uploader_timer.start()

        # If no media files provided, upload all from optimized_media folder
        if media_files == []:
            optimized_medias = Path(path_manager.optimized_media)
            media_files = [Path(media) for media in optimized_medias.iterdir()]
        print(media_files)

        for media in media_files:
            success = _upload_media(media, count)
            count += 1

            if not success:
                count_failed += 1

        # Adjust count to be the total number of files processed
        count -= 1

    except Exception as e:
        log_message(f"{e}", path_manager.log)
    finally:
        uploader_timer.stop()
        log_message(f"Upload process ended - Google Photos. Elapsed: {uploader_timer}", path_manager.log)
        log_message(f"Upload Summary: Success: {count - count_failed}, Failed: {count_failed}, Total: {count}", path_manager.log)



# MAIN (Manual Run)
if __name__ == "__main__":
    upload_all_medias()
