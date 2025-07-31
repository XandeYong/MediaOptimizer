import re
from pathlib import Path
from datetime import datetime

class FileManager:
    @staticmethod
    def sanitize_filename(name: str):
        """
        Ensure filenames are safe by replacing invalid characters.

        Args:
            name (str): The original filename.

        Returns:
            str: A sanitized, filesystem-safe filename.
        """
        return re.sub(r'[^\w\-]', '_', name)

    @staticmethod
    def generate_folder_structure(base_folder="output", name=""):
        """
        Generate a unique folder path based on a timestamp and optional name.

        Args:
            base_folder (str): Base directory to create the folder in.
            name (str): Optional name prefix for the folder.

        Returns:
            Path: The full path to the created folder.
        """
        timestamp = datetime.today().strftime('%Y-%m-%d_%H%M%S')
        folder = Path(base_folder)
        folder.mkdir(parents=True, exist_ok=True)

        item_count = sum(1 for _ in folder.iterdir()) + 1

        if name and not name.endswith("-"):
            name += "-"

        folder_path = folder / f"{name}{timestamp}-{item_count}"
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    @staticmethod
    def generate_file(file_name: str, base_folder="", extension="txt"):
        """
        Create a new file with a sanitized name in the specified folder.

        Args:
            file_name (str): Desired filename (without extension).
            base_folder (str): Directory in which to create the file.
            extension (str): File extension (default is 'txt').

        Returns:
            Path: Path to the newly created file.
        """
        safe_file_name = FileManager.sanitize_filename(file_name)
        file = Path(base_folder) / f"{safe_file_name}.{extension}"
        file.touch()
        return file

    @staticmethod
    def generate_folder_single(folder_name="", base_folder=Path("")):
        """
        Create a single folder (not timestamped) within a base directory.

        Args:
            folder_name (str): Name of the new folder.
            base_folder (Path): Directory to create the folder in.

        Returns:
            Path: The full path to the created folder.
        """
        folder = base_folder / folder_name
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def collect_media_files(root_dir: Path, image_exts=None, video_exts=None):
        """
        Recursively scans a folder for image and video files.

        Args:
            root_dir (Path): The root directory to scan.
            image_exts (list[str], optional): Allowed image file extensions.
            video_exts (list[str], optional): Allowed video file extensions.

        Returns:
            media_files (list[Path]): List of media file paths found.
            image_count (int): number of image found.
            video_count (int): number of video found.
        """
        if image_exts is None:
            image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
        if video_exts is None:
            video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']

        image_exts = set([ext.lower() for ext in image_exts])
        video_exts = set([ext.lower() for ext in video_exts])

        image_count = 0
        video_count = 0
        media_files = []

        def found(file):
            media_files.append(file)
            return 1

        for file_path in root_dir.rglob('*'):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lower()
            if ext in image_exts:
                image_count += found(file_path)
            elif ext in video_exts:
                video_count += found(file_path)

        # allowed_exts = set(ext.lower() for ext in image_exts + video_exts)
        # return [
        #     file_path
        #     for file_path in root_dir.rglob('*')
        #     if file_path.is_file() and file_path.suffix.lower() in allowed_exts
        # ]

        return media_files, image_count, video_count
