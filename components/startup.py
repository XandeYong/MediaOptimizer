import argparse
import json
from dependency_injector import containers, providers
from classes.google_auth import GoogleAuth
from classes.tools import Tools
from classes.path_manager import PathManager
from components.google_api_manager import GoogleAPIManager
from components.media_optimizer import MediaOptimizer
from components.file_manager import FileManager

# Args handling
parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, help="Operation Mode (Default: Manual)")
parser.add_argument("--path", type=str, help="Provide the folder path to skip the interaction with the console")
args = parser.parse_args()

mode = args.mode or "Manual"
user_input = args.path or None

# Configuration
config: str
with open('config.json', 'r') as file:
    config = json.load(file)

google_auth = GoogleAuth(**config['google_auth'])
tools = Tools(**config['tool'])


# File Generation
folder_path = FileManager.generate_folder_structure(name=mode)
log_file = FileManager.generate_file("log", folder_path, extension="txt")
failed_file = FileManager.generate_file("fail", folder_path, extension="txt")
failed_media_folder = FileManager.generate_folder_single("failed_media", folder_path)
optimized_media_folder = FileManager.generate_folder_single("optimized_media", folder_path)
raw_media_folder = FileManager.generate_folder_single("raw_media", folder_path)
path_manager = PathManager(folder_path, log_file, failed_file, failed_media_folder, optimized_media_folder, raw_media_folder)

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
    tools = providers.Singleton(Tools)

container = Container()
container.path_manager = path_manager
container.google_api_manager = google_api_manager
container.media_optimizer = media_optimizer
container.google_auth = google_auth
container.tools = tools
