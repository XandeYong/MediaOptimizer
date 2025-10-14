from mediaoptimizer import container
from classes.google_auth import GoogleAuth
from classes.path_manager import PathManager
from components.my_logging import log_message
import requests
import os

# Injecting dependency
path_manager: PathManager = container.path_manager
google_auth: GoogleAuth = container.google_auth

# Set up API credentials
ACCESS_TOKEN = google_auth.access_token_read
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
UPLOAD_URL = google_auth.upload_media_api
CREATE_MEDIA_URL = google_auth.create_media_api

# Variables
count_success = 0
count_failed = 0

def upload_photo(file_path):
    file_name = os.path.basename(file_path)
    print(file_name)
    exit()

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
            log_message(f"Upload token request failed for {file_name}: {upload_response.text}", path_manager.failed_log)
            return None

        return upload_response.text.strip()  # This is the upload token
    except Exception as e:
        log_message(f"Error reading file {file_name}: {e}", path_manager.failed_log)
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
        log_message(f"Failed to create media item: {file_name}", path_manager.failed_log)
        log_message(f"Error: {response.text}", path_manager.failed_log)
        count_failed += 1

def upload_all_photos():
    log_message("Upload process started.", path_manager.log)

    for file_name in os.listdir(path_manager.optimized_media):
        file_path = path_manager.failed_media / file_name

        if not file_path.is_file():
            continue

        log_message(f"Processing file: {file_name}", path_manager.log)
        upload_token = upload_photo(file_path)

        if upload_token:
            create_media_item(upload_token, file_name)
        else:
            count_failed += 1

    log_message(f"Upload Summary:\nSuccess: {count_success}\nFailed: {count_failed}\nTotal: {count_success + count_failed}", path_manager.log)
    log_message("Upload process ended.", path_manager.log)

# MAIN (Manual Run)
if __name__ == "__main__":
    upload_all_photos()
