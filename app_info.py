APP_NAME = "Media Optimizer"
VERSION = "1.3.0.0"
BUILD_DATE = "2025-07-18T10:00:00Z"
AUTHOR = "XandeYong"

# My tools version
TOOL_VERSIONS = {
    "ffmpeg": "7.1.1",
    "ffprobe": "7.1.1",
    "exiftool": "13.30"
}

DEPENDENCIES = {
    "python": "3.13.2"
}

ENVIRONMENT = {
    "os": "Windows",
    "arch": "x86_64"
}

"""
# Version History

1.0.0.0
- Created MediaOptimizer

1.1.0.0
- AVIF support
- HEIF support
- Introduced 10 arguments (-h to study them)

1.2.0.0
- Introduced retry-failed arguments
- Created versioning_specification.md
- Delete failed incomplete file that was generate into optimized_media folder
- Allow user to interrupt the current process (ctrl-c)
- Added codec mapping and extension_helper to work on codec, mime and ext convertion
- Handle mkv metadata modification
- Description update on arguments (iof > ioc, vof > voc)

1.2.1.0
- Fixed image_output_codec and video_output_codec not working
- rename main.py to mediaoptimizer.py

1.3.0.0
- Publish media to Google Photos
- Added 1 argument (operation) to allow user to choose operation between (0: all, 1: optimize only, 2: upload only)
- Added 2 folders to manage uploaded and failed upload media
- Removed failed_log file
- Allow single file optimization and upload to Google Photos
- Fixed AVIF optimization issue
- Fixed failed to delete incomplete optimized media file when optimization failed
- Fixed video optimization interruption issue (subprocess not handled properly)
- Created 2 test cases (test_extension.py, test_magic.py) and added test data files
- Added pyproject.toml for project management

[Future Release]
x.x.0.0
- Async version of optimizer part

"""