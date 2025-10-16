import os
import shutil
import uuid
import requests
from mediaoptimizer import container
from classes.path_manager import PathManager
from components.google_api_manager import GoogleAPIManager
from components.my_logging import log_message
from helper.timespan_logger import TimeSpanLogger
from pathlib import Path

# Injecting dependency
path_manager: PathManager = container.path_manager
google_api_manager: GoogleAPIManager = container.google_api_manager

# Set up API credentials
# ACCESS_TOKEN = google_api_manager._creds.token
# HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
# UPLOAD_URL = google_api_manager.upload_media_api
# CREATE_MEDIA_URL = google_api_manager.create_media_api

# Variables
count_success = 0
count_failed = 0

def upload_media(file_path):
    file_name = os.path.basename(file_path)
    print(file_name)
    # exit()

    # Step 1: Upload the file to get an upload token
    log_message(f"Uploading {file_name} to get upload token...", path_manager.log)
    headers = {
        **HEADERS,
        "Content-Type": "application/octet-stream",
        "X-Goog-Upload-File-Name": file_name,
        "X-Goog-Upload-Protocol": "raw",
    }

    try:
        with open(file_path, "rb") as file:
            upload_response = requests.post(UPLOAD_URL, headers=headers, data=file)

        if upload_response.status_code != 200:
            log_message(f"Upload token request failed for {file_name}: {upload_response.text}", path_manager.log)
            return None

        return upload_response.text.strip()  # This is the upload token
    except Exception as e:
        log_message(f"Error reading file {file_name}: {e}", path_manager.log)
        return None

def create_media_item(upload_token, file_name):
    global count_success, count_failed

    payload = {
        "newMediaItems": [
            {
                "description": f"Uploaded: {file_name}",
                "simpleMediaItem": {
                    "uploadToken": upload_token
                }
            }
        ]
    }

    response = requests.post(CREATE_MEDIA_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        log_message(f"Successfully created media item: {file_name}", path_manager.log)
        count_success += 1
    else:
        log_message(f"Failed to create media item: {file_name}", path_manager.log)
        log_message(f"Error: {response.text}", path_manager.log)
        count_failed += 1

def upload_all_medias(media_files: list[Path]):
    try:
        log_message("Upload process started - Google Photos", path_manager.log)
        uploader_timer = TimeSpanLogger()
        uploader_timer.start()
        
        count_failed = 0
        count_success = 0

        if media_files == []:
            optimized_medias = Path(path_manager.optimized_media)
            media_files = [Path(media) for media in optimized_medias.iterdir()]
        print(media_files)

        count: int = 1
        success: bool = False
        guid = str(uuid.uuid4())
        timer = TimeSpanLogger()

        for media in media_files:
            try:
                log_message(f"[{guid}] Start processing file: [{count}], media: [{media.name}], path: [{media.absolute()}]", path_manager.log)
                timer.start()
                # file_path = path_manager.optimized_media / media
                print(media)
                # raise Exception("Debug stop")

                if not media.is_file():
                    continue

                log_message(f"Processing file: {media}", path_manager.log)
                upload_token = google_api_manager.upload_media(media)
                log_message(f"Processing file: {media}", path_manager.log)

                if upload_token:
                    log_message(f"Creating media item: {media}", path_manager.log)
                    response = google_api_manager.create_media_item(upload_token, media.name)
                    log_message(f"Response: {response}", path_manager.log)
                    count_success += 1
                    shutil.move(media, path_manager.uploaded_media)
                else:
                    log_message(f"Failed to upload media: {media}", path_manager.log)
                    count_failed += 1
                    shutil.move(media, path_manager.failed_upload_media)

                count += 1
                
            except Exception as e:
                log_message(f"[{guid}] Error: {e}", path_manager.log)

        uploader_timer.stop()
        log_message(f"Upload process ended - Google Photos. Elapsed: {uploader_timer}", path_manager.log)
        log_message(f"Upload Summary: Success: {count_success}, Failed: {count_failed}, Total: {count_success + count_failed}", path_manager.log)
        
    except Exception as e:
        raise e

# MAIN (Manual Run)
if __name__ == "__main__":
    upload_all_medias()
