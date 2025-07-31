from components.startup import container, user_input
from components.my_logging import log_message
from classes.google_auth import GoogleAuth
from classes.path_manager import PathManager
from components.file_manager import FileManager
from pathlib import Path
from constants.media_mime_types import IMAGE_EXT, VIDEO_EXT

# Injecting dependency
path_manager: PathManager = container.path_manager
google_auth: GoogleAuth = container.google_auth

# MAIN
if __name__ == "__main__":
    # Start Application
    log_message("Media Optimizer application started.", path_manager.log)
    log_message(f"Log file path: {path_manager.log}", path_manager.log)
    log_message(f"Fail file path: {path_manager.failed_log}", path_manager.log)

    # Perform Download
    # from modules.download_files import google_download
    # google_download()

    if user_input is None:
        user_input = input("Enter the folder path: ")
    log_message(f"User Input: {user_input}", path_manager.log)
    media_files, image_count, video_count = FileManager.collect_media_files(Path(user_input), IMAGE_EXT, VIDEO_EXT)
    # print(media_files)
    log_message(f"Total files: {len(media_files)}, image: {image_count}, video: {video_count}", path_manager.log)

    # Perform Optimize
    from modules.optimizer import process_medias
    process_medias(media_files)

    # Perform Upload


    # End Application
    log_message("Media Optimizer application ended.", path_manager.log)
