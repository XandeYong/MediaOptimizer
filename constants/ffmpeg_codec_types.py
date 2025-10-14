"""
    MEDIA_CODECS defines the mapping between media codecs and their associated MIME types.

    A *codec* (short for *coder-decoder*) is a method used to encode or decode digital media data — 
    such as audio, video, or image streams. Codecs determine how raw data is compressed, stored, and reproduced.

    In modern media systems (e.g., FFmpeg, multimedia players, and encoders), each codec corresponds to a 
    specific compression algorithm and often aligns with a particular container format (e.g., MP4, MKV, WebM).

    This mapping bridges the relationship between codec identifiers (e.g., "libx264", "mjpeg", "flac") 
    and their MIME types (e.g., "video/mp4", "image/jpeg", "audio/flac"). 

    It enables the system to:
      - Dynamically infer file types from codec metadata.
      - Choose the appropriate encoder during media optimization.
      - Maintain consistent handling of lossy and lossless formats across workflows.

    In short, MEDIA_CODECS standardizes codec-MIME relationships, ensuring consistent 
    encoding, decoding, and file-type recognition across the media processing pipeline.
"""
# Map FFmpeg codecs to MIME types
FFMPEG_CODEC_TYPES = {
    # === Image Codecs ===
    "mjpeg": "image/jpeg",                # JPEG (lossy)
    "ljpeg": "image/jpeg",                # JPEG (lossless variant)
    "libjxl": "image/jxl",                # JPEG XL (lossless/lossy hybrid)
    "png": "image/png",                   # PNG (lossless)
    "hevc": "image/heic",                 # HEIC/HEIF (HEVC)
    "libaom-av1": "image/avif",           # AVIF (AV1)
    "libsvtav1": "image/avif",            # AVIF alt encoder
    "gif": "image/gif",                   # Animated GIF
    "bmp": "image/bmp",                   # Bitmap
    "libwebp": "image/webp",              # WebP (lossy)
    "libwebp_lossless": "image/webp",     # WebP (lossless)
    "tiff": "image/tiff",                 # TIFF
    "ico": "image/x-icon",                # Windows icon

    # === Video Codecs ===
    "libx264": "video/mp4",               # H.264 (lossy)
    "libx264rgb": "video/mp4",            # H.264 lossless mode
    "libx265": "video/mp4",               # H.265 (lossy/lossless capable)
    "libx265-lossless": "video/mp4",      # (alias for lossless param usage)
    "mpeg4": "video/avi",                 # MPEG-4 Part 2
    "mpeg2video": "video/mpeg",           # MPEG-2
    "prores": "video/quicktime",          # Apple ProRes
    "prores_ks": "video/quicktime",       # Alt encoder
    "wmv2": "video/x-ms-wmv",             # WMV
    "flv": "video/x-flv",                 # Flash Video
    "libvpx": "video/webm",               # VP8
    "libvpx-vp9": "video/webm",           # VP9
    "libtheora": "video/ogg",             # Theora (Ogg)

    # === Audio Codecs ===
    "libmp3lame": "audio/mpeg",           # MP3
    "pcm_s16le": "audio/wav",             # WAV (uncompressed)
    "pcm_s24le": "audio/wav",             # High depth WAV
    "libopus": "audio/ogg",               # Opus
    "flac": "audio/flac",                 # FLAC (lossless)
    "aac": "audio/aac",                   # AAC (lossy)
    "libfdk_aac": "audio/aac",            # High-quality AAC encoder

    # === Misc / Unsupported ===
    "none": "application/octet-stream",   # Fallback/unknown
}

# CONSTANT CODEC
IMAGE_CODEC, VIDEO_CODEC, AUDIO_CODEC = [], [], []
for codec, mime in FFMPEG_CODEC_TYPES.items():
    if mime.startswith("image/"):
        IMAGE_CODEC.append(codec)
    elif mime.startswith("video/"):
        VIDEO_CODEC.append(codec)
    elif mime.startswith("audio/"):
        AUDIO_CODEC.append(codec)

#IMAGE_CODEC = [codec for codec, mime in FFMPEG_CODEC_TYPES.items() if mime.startswith("image/")]
#VIDEO_CODEC = [codec for codec, mime in FFMPEG_CODEC_TYPES.items() if mime.startswith("video/")]
#AUDIO_CODEC = [codec for codec, mime in FFMPEG_CODEC_TYPES.items() if mime.startswith("audio/")]

## Example Usage
# codec = "libaom-av1"
# mime_type = FFMPEG_CODEC_TYPES.get(codec, "")
# print(f"Codec mime-type for {codec}: {mime_type}")