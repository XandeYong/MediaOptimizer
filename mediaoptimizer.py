from components.startup import container
from components.my_logging import log_message
from classes.argument import Argument
from classes.google_auth import GoogleAuth
from classes.path_manager import PathManager
from components.file_manager import FileManager
from pathlib import Path
from constants.media_mime_types import IMAGE_EXT, VIDEO_EXT

# Injecting dependency
args: Argument = container.args
path_manager: PathManager = container.path_manager
google_auth: GoogleAuth = container.google_auth

def set_supported_ext(extensions: list[str]):
    image_ext = []
    video_ext = []
    unsupported_extension = []

    if extensions:
        image_ext_constant = {ext.lower() for ext in IMAGE_EXT}
        video_ext_constant = {ext.lower() for ext in VIDEO_EXT}

        for ext in extensions:
            ext = ext.lower()
            ext = f".{ext}" if not ext.startswith('.') else ext  # normalize
            if ext in image_ext_constant:
                image_ext.append(ext)
            elif ext in video_ext_constant:
                video_ext.append(ext)
            else:
                unsupported_extension.append(ext)
    else:
        image_ext = IMAGE_EXT
        video_ext = VIDEO_EXT

    if unsupported_extension:
        raise(f'Unsupported extension: {", ".join(unsupported_extension)}')
    
    return image_ext, video_ext

# MAIN
if __name__ == "__main__":
    # Start Application
    log_message("Media Optimizer application started.", path_manager.log)
    try:
        log_message(f"Log file path: {path_manager.log}", path_manager.log)
        log_message(f"Args: {args.model_dump_json()}", path_manager.log)

        # Perform Download
        # from modules.download_files import google_download
        # google_download()

        source = args.source
        if source is None:
            source = input("Enter the folder path: ")
        log_message(f"Source: {source}", path_manager.log)
        
        # Filter media
        image_ext, video_ext = set_supported_ext(args.extension)
        media_files, image_count, video_count = FileManager.collect_media_files(Path(source), image_ext, video_ext, args.media)

        # print(media_files)
        log_message(f"Total files: {len(media_files)}, image: {image_count}, video: {video_count}", path_manager.log)

        # Perform Optimize
        if args.operation in (0, 1):
            from modules.optimizer import process_medias
            process_medias(media_files)

        # Perform Upload
        if args.operation in (0, 2):
            from modules.upload_files import upload_all_medias
            upload_all_medias(media_files if args.operation == 2 else [])

    except Exception as e:
        log_message(f"{e}", path_manager.log)

    # End Application
    log_message("Media Optimizer application ended.", path_manager.log)
