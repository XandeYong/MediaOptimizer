"""
    MEDIA_MIME_TYPES (Media Multipurpose-Internet-Mail-Extensions type) is a standard meta-data information for files
    to be recognize by system. 

    MIME type stands for Multipurpose Internet Mail Extensions type. 
    It's a standardized way to indicate the nature and format of a file — originally designed for email, 
    but now used everywhere (web, file uploads, APIs, etc.).

    Specifies and identify the MINE type for a file allow the system to recognize 
    and perform read-write action on the selected file to its full extent.
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