APP_NAME = "Media Optimizer"
VERSION = "1.1.0.0"
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

[Future Release]
1.x.0.0
- Publish to Google Photos
- Async version of optimizer part

"""