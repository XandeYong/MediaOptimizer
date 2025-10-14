import argparse
import json
import sys
from pydantic import ValidationError
from dependency_injector import containers, providers
from classes.google_auth import GoogleAuth
from classes.tools import Tool
from classes.argument import Argument
from classes.path_manager import PathManager
from components.google_api_manager import GoogleAPIManager
from components.media_optimizer import MediaOptimizer
from components.file_manager import FileManager

# Args handling
parser = argparse.ArgumentParser(description="MediaOptimizer settings")
parser.add_argument("-n", "--name", type=str, default="Manual", help="Operation name (default: 'Manual')")
parser.add_argument("-s", "--source", type=str, help="Source folder path (skips manual input)")
parser.add_argument("-iq", "--image_quality", type=int, help="Image quality (int value, depends on selected codec)")
parser.add_argument("-vq", "--video_quality", type=int, help="Video quality (int value, depends on selected codec)")
parser.add_argument("-ioc", "--image_output_codec", type=str, help="Image output codec (mjpeg, png, libaom-av1, libwebp), look into your ffmpeg encoders for more codec.")
parser.add_argument("-voc", "--video_output_codec", type=str, help="Video output codec (libx265, libx264, flv, wmv2), look into your ffmpeg encoders for more codec.")
parser.add_argument("-m", "--media", type=str, choices=["image", "video"], help="Only process specified media type")
parser.add_argument("-e", "--extension", type=str, help='Only process files with specified extensions (e.g. "jpg;png;mp4")')
parser.add_argument("-k", "--keep_temp", action="store_true", help='Keep temp files instead of deleting them after execution (large files in png format)')
parser.add_argument("-rp", "--allow_reprocess", action="store_true", help='Allow reprocessing files that are previously processed or flagged')
parser.add_argument("-rf", "--retry_failed", action="store_true", help='Retry failed files (recommend on small batch of files)')
args = parser.parse_args()


try:
    args_model = Argument(
        name = args.name,
        source = args.source,
        image_quality = args.image_quality,
        video_quality = args.video_quality,
        image_output_format = args.image_output_format,
        video_output_format = args.video_output_format,
        media = args.media,
        extension = args.extension.split(';') if isinstance(args.extension, str) else args.extension,
        keep_temp = args.keep_temp,
        allow_reprocess = args.allow_reprocess,
        retry_failed = args.retry_failed
    )
except ValidationError as e:
    print(e)
    print(e.json(indent=2))
    sys.exit(1)


# Configuration
config: str
with open('config.json', 'r') as file:
    config = json.load(file)

google_auth = GoogleAuth(**config['google_auth'])
tools = Tool(**config['tool'])


# File Generation
folder_path = FileManager.generate_folder_structure(name=args.name)
log_file = FileManager.generate_file("log", folder_path, extension="txt")
failed_file = FileManager.generate_file("fail", folder_path, extension="txt")
failed_media_folder = FileManager.generate_folder_single("failed_media", folder_path)
temp_media_folder = FileManager.generate_folder_single("temp_media", folder_path)
optimized_media_folder = FileManager.generate_folder_single("optimized_media", folder_path)
raw_media_folder = FileManager.generate_folder_single("raw_media", folder_path)
path_manager = PathManager(folder_path, log_file, failed_file, failed_media_folder, temp_media_folder, optimized_media_folder, raw_media_folder)

# Init Manager
google_api_manager = GoogleAPIManager(
    client_secret_file=google_auth.file_path.client_secret_file,
    token_file=google_auth.file_path.token_file,
    validate_token_url=google_auth.google_api.validate_token_url,
    media_upload_url=google_auth.google_api.media_upload_url,
    media_create_url=google_auth.google_api.media_create_url,
    token_scopes=[google_auth.scope.appendonly]
)

media_optimizer = MediaOptimizer(
    ffmpeg=tools.ffmpeg, ffprobe=tools.ffprobe,
    exiftool=tools.exiftool, xmp_config=tools.config.exiftool_config
)

# Validate Tools
exiftool = media_optimizer.get_exiftool_version
ffmpeg = media_optimizer.get_ffmpeg_version
ffprobe = media_optimizer.get_ffprobe_version


# Setup Dependency Injection
class Container(containers.DeclarativeContainer):
    path_manager = providers.Singleton(PathManager)
    google_api_manager = providers.Singleton(GoogleAPIManager)
    media_optimizer = providers.Singleton(MediaOptimizer)
    google_auth = providers.Singleton(GoogleAuth)
    tools = providers.Singleton(Tool)
    args = providers.Singleton(Argument)

container = Container()
container.path_manager = path_manager
container.google_api_manager = google_api_manager
container.media_optimizer = media_optimizer
container.google_auth = google_auth
container.tools = tools
container.args = args_model
