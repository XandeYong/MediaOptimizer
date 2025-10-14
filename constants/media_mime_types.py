"""
    MEDIA_MIME_TYPES defines the mapping between MIME types and their corresponding file extensions.

    A *MIME type* (Multipurpose Internet Mail Extensions type) is a standardized identifier that 
    indicates the nature and format of a file. Originally created for email attachments, MIME types 
    are now widely used across operating systems, web servers, APIs, and file management systems 
    to classify and handle files appropriately.

    This mapping establishes the relationship between MIME identifiers (e.g., "image/jpeg", "video/mp4") 
    and file extensions (e.g., ".jpg", ".mp4"). 

    It allows the system to:
      - Recognize the type of media being processed.
      - Infer correct file extensions when encoding or saving files.
      - Ensure consistent file type detection across different platforms and workflows.
      - Support automated media-type handling in optimization, transcoding, and metadata operations.

    In short, MEDIA_MIME_TYPES standardizes MIME-to-filetype associations, enabling 
    reliable file recognition, consistent naming, and smooth interoperability across media systems.
"""
# All Media Types
MEDIA_MIME_TYPES = {
    # Image formats
    "image/jpeg": ".jpg",
    "image/jxl": ".jxl",
    "image/png": ".png",
    "image/heic": ".HEIC",
    "image/heif": ".HEIF",
    "image/avif": ".avif",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/webp": ".webp",
    "image/tiff": ".tiff",
    "image/svg+xml": ".svg",
    "image/x-icon": ".ico",
    "image/x-adobe-dng": ".dng",
    
    # Video formats
    "video/mp4": ".mp4",
    "video/mkv": ".mkv",
    "video/avi": ".avi",
    "video/mpeg": ".mpg",
    "video/quicktime": ".mov",
    "video/x-ms-wmv": ".wmv",
    "video/x-flv": ".flv",
    "video/webm": ".webm",
    "video/ogg": ".ogv",
    
    # Audio formats (optional, since some media include audio)
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "audio/ogg": ".ogg",
    "audio/flac": ".flac",
    "audio/aac": ".aac",
    
    # Other formats (optional)
    "application/pdf": ".pdf",
    "application/zip": ".zip",
    "application/octet-stream": ".bin", # also mean unknown if the format is undetermined
}

# CONSTANT Extension
IMAGE_EXT, VIDEO_EXT, AUDIO_EXT = [], [], []
for mime, ext in MEDIA_MIME_TYPES.items():
    if mime.startswith("image/"):
        IMAGE_EXT.append(ext)
    elif mime.startswith("video/"):
        VIDEO_EXT.append(ext)
    elif mime.startswith("audio/"):
        AUDIO_EXT.append(ext)

# Same as .jpg
IMAGE_EXT.append(".jpeg")

#IMAGE_EXT = [MEDIA_MIME_TYPES[mime] for mime in MEDIA_MIME_TYPES if mime.startswith("image/")]
#VIDEO_EXT = [MEDIA_MIME_TYPES[mime] for mime in MEDIA_MIME_TYPES if mime.startswith("video/")]
#AUDIO_EXT = [MEDIA_MIME_TYPES[mime] for mime in MEDIA_MIME_TYPES if mime.startswith("audio/")]

## Example Usage
# mime_type = "video/mp4"
# file_extension = MEDIA_MIME_TYPES.get(mime_type, "")
# print(f"File extension for {mime_type}: {file_extension}")