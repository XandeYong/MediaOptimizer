from mediaoptimizer import container
from classes.google_auth import GoogleAuth
from classes.path_manager import PathManager
from components.my_logging import log_message
from modules.optimizer import process_medias
import requests
import threading
import time
from PIL import Image
from constants.media_mime_types import MEDIA_MIME_TYPES


# # Injecting dependency
path_manager: PathManager = container.path_manager
google_auth: GoogleAuth = container.google_auth

# Set up API credentials
ACCESS_TOKEN = google_auth.scope.readonly.token
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
GOOGLE_API = google_auth.google_api.media_fetch_url

# variables
count_success = 0
count_failed = 0

# Function to fetch media items
def fetch_media():
    log_message("Starting API call...", path_manager.log)
    response = requests.get(url=GOOGLE_API, headers=HEADERS)
    log_message("API call completed.", path_manager.log)

    if response.status_code == 200:
        log_message("Fetch media API success.", path_manager.log)
        with open(f"{path_manager.root}/media_content.json", "w") as file:
            file.write(response.text)
        return response.json().get("mediaItems", [])
    else:
        log_message(f"Fetch media API failed with status: {response.status_code}", path_manager.log)
        return []

# Function to download media
def download_media(media_items):
    global count_success, count_failed

    log_message("Starting media download...", path_manager.log)
    for item in media_items:
        url = item["baseUrl"]
        extension = MEDIA_MIME_TYPES.get(item["mimeType"]) or (".jpg" if item['mimeType'].startswith('image') else ".mp4")
        file_name = f"{item['filename']}{extension}"
        file_path = path_manager.failed_media / file_name

        log_message(f"Downloading {file_name}...", path_manager.log)
        media_response = requests.get(url)

        if media_response.status_code == 200:
            with open(path_manager.failed_media / file_name, "wb") as file:
                file.write(media_response.content)

            # add Google ID into the metadata
            img = Image.open(file_path)
            img.info["Google ID"] = item['id']
            img.save(file_path)

            log_message(f"Success: {file_name}", path_manager.log)
            count_success += 1

            # Start optimization in a new thread
            thread = threading.Thread(target=process_medias, args=(file_name, item["mimeType"]))
            thread.start()
        else:
            log_message(f"Failed: {file_name}", path_manager.log)
            log_message(f"Failed: {file_name}", path_manager.failed_log)
            count_failed += 1

    log_message("Download process completed.", path_manager.log)

# MAIN function
def google_download():
    log_message("Download process started.", path_manager.log)

    media_items = fetch_media()
    if media_items:
        download_media(media_items)
        log_message(f"Summary:\nSuccess: {count_success}\nFailed: {count_failed}\nTotal: {count_success + count_failed}", path_manager.log)
    else:
        log_message("No media items found.", path_manager.log)

    log_message("Process ended.", path_manager.log)

# MAIN (Manual Run)
if __name__ == "__main__":
    google_download()
