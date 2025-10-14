from constants.ffmpeg_codec_types import FFMPEG_CODEC_TYPES
from constants.media_mime_types import MEDIA_MIME_TYPES

class ExtensionHelper:

    @staticmethod
    def get_extension_from_mime(mime: str):
        """
        Resolve the appropriate file extension for a given mime.
        Falls back to '.bin' if not recognized.
        """
        default = ".bin"
        return MEDIA_MIME_TYPES.get(mime, default)
    
    @staticmethod
    def get_extension_from_codec(codec: str):
        """
        Resolve the appropriate file extension for a given FFmpeg codec.
        Falls back to '.bin' if not recognized.
        """
        default = ".bin"
        mime = FFMPEG_CODEC_TYPES.get(codec)
        if not mime:
            return default

        return MEDIA_MIME_TYPES.get(mime, default)
    
    @staticmethod
    def get_codec_from_extension(ext: str):
        """
        Resolve the appropriate FFmpeg codec for a given file extension.
        Falls back to 'application/octet-stream' if not recognized.
        """
        default = "application/octet-stream"
        mime = MEDIA_MIME_TYPES.get(ext)
        if not mime:
            return default

        return FFMPEG_CODEC_TYPES.get(mime, default)
    



# when have time will merge with logging (not necessary to seperate timer and logging in this project)