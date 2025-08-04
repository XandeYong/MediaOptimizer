import subprocess
import os
import re
import json
from pathlib import Path
from tqdm import tqdm

class MediaOptimizer:
    def __init__(self, ffmpeg="ffmpeg", ffprobe="ffprobe", exiftool="exiftool", xmp_config=None):
        self._ffmpeg:str = ffmpeg
        self._ffprobe:str = ffprobe
        self._exiftool:str = exiftool
        self._xmp_config:str = xmp_config

    #region Loader
    def load_executable(self, ffmpeg=None, ffprobe=None, exiftool=None):
        if ffmpeg:
            self._ffmpeg = ffmpeg
        if ffprobe:
            self._ffprobe = ffprobe
        if exiftool:
            self._exiftool = exiftool

    def load_xmp_config(self, xmp_config):
        self._xmp_config = xmp_config
    #endregion

    #region Metadata
    def get_mime_type(self, filepath: Path):
        cmd = [
            self._exiftool,
            "-MIMEType", str(filepath)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"ExifTool failed: {result.stderr.strip()}")
        
        for line in result.stdout.splitlines():
            if line.startswith("MIME Type"):
                return line.split(":", 1)[1].strip()
        return None

    def set_media_metadata(self, filepath: Path, namespace: str, metadatas: dict[str, str], xmp_config: bool=False):
        if metadatas:
            cmd = [
                self._exiftool,
                *(["-config", self._xmp_config] if xmp_config else [])
            ]
            
            for tag, value in metadatas.items():
                cmd.append(f"-XMP-{namespace}:{tag}={value}")  #-XMP-ID:Google_ID
            
            cmd.extend([
                "-overwrite_original",
                str(filepath)
            ])

            result = subprocess.run(cmd, check=True)
            return result
        return None
    
    def read_custom_xmp_tag(self, file_path: str, namespace:str, tag: str, xmp_config: str=None):
        cmd = [
            self._exiftool,
            "-config", xmp_config or self._xmp_config,
            f"-XMP-{namespace}:{tag}",
            "-j", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)[0]
        
        return data.get(tag)

    def replace_metadata(self, from_file, to_file):
        """
        Copies all metadata (EXIF, IPTC, GPS, etc.) from an input image to an output JPEG.

        This uses exiftool to transfer metadata from the original image (input_path)
        to the optimized/compressed image (output_path), and overwrites the output's existing metadata.

        Args:
            from_file (str): Path to the source image containing the desired metadata.
            to_file (str): Path to the image that should receive the metadata. If None,
                            defaults to the same name as input_path but with a .jpg extension.

        """

        cmd = [
            self._exiftool,              # Path to exiftool binary (e.g., "/usr/bin/exiftool")
            "-TagsFromFile", from_file,  # Copy all metadata from input file
            "-all:all",                  # Copy all groups of metadata (EXIF, IPTC, XMP, etc.)
            "-overwrite_original",       # Overwrite output image's original metadata
            to_file                      # File to receive the metadata
        ]
        subprocess.run(cmd, check=True)
    #endregion
    
    #region Optimize Image
    def optimize_image(self, input_path: str, output_path:str = None, qvb: int = 4, crf: int = 30, codec="libaom-av1"):
        """
        Converts an image to optimized JPEG using FFmpeg.
        
        Args:
            input_path (str): Path to the input image.
            mime_type (str): Image mimetype.
            output_path (str, optional): Path to save the JPEG. Defaults to input file name with .jpg.
            qvb (int): Quality for Variable Bitrate, simpler codecs quality (1=best, 31=worst). Lower is better, 4 is reasonable.
            crf (int): Constant Rate Factor, modern codecs quality (0=best, 63=worst). Lower is better, 30 is reasonable
            codec (str): can study ffmpeg codec list to choose codec of your liking. Suggest mjpeg or libaom-av1 for smallest file size (Default: libaom-av1)
            metadata (bool): Keep metadata (True to keep previous image's metadata, False to let it be).
        """
        ext = ".jpg" if codec == "mjpeg" else ".avif"
        output_path = os.path.splitext(output_path or input_path)[0] + ext

        cmd = [
            self._ffmpeg,
            "-y",                    # Overwrite output without asking
            "-i", input_path,        # Input file
            "-map_metadata", "0",    # Keep original metadata
            "-c:v", codec,           # Output format
            "-update", "1",          # overwrite the output file if it exists (used for image outputs)
        ]

        modern_codecs = {"libaom-av1", "libsvtav1", "libx264", "libx265"}
        if codec in modern_codecs:
            cmd += [
                "-crf", str(crf),         # Constant Rate Factor (quality)
                "-still-picture", "1",    # AVIF required standards compliance
            ]    
        else:
            cmd += [
                "-q:v", str(qvb),         # Quality for Variable Bitrate (quality)
                "-frames:v", "1",         # Force format
            ]

        cmd += [output_path]         # Output file

        mod_time = os.path.getmtime(input_path)

        subprocess.run(cmd, check=True)
        os.utime(output_path, (mod_time, mod_time))

        return output_path

    # Get progress bar
    def get_video_duration(self, filepath):
        """Get video duration in seconds using ffprobe."""
        cmd = [
                self._ffprobe, "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", filepath
        ]
        print(cmd)
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    #endregion

    #region Optimize Video
    def optimize_video(self, 
        input_path: str,
        output_path: str = None,
        crf: int = None,
        preset: str = "slow",
        codec: str = "libx265",
        audio_bitrate: str = "128k",
        scale_resolution: str = None,
        streaming: bool = False,
        metadata: bool = True
    ):
        """
        Reduce video file size using FFmpeg while keeping quality acceptable.

        Args:
            input_path (str): Full path to the input video file.
            output_path (str): Path to save optimized video. If None, appends '_optimized.mp4' to input filename.
            crf (int): Constant Rate Factor Profile, Default value will based on codex ('libx264' = 23, 'libx265' = 26). 
                       CRF (lower = better quality, bigger size). Recommended: 18–28.
            preset (str): Encoding speed vs compression efficiency.
                        Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow.
            codex (str): Encoding format. Recommend 'libx264' for compatibility, but if required smaller file size
                        highly recommend 'libx265' but beware of compatibility, old device will but be able to open it.
                        Default value: 'libx265'.
            audio_bitrate (str): Bitrate for audio stream. e.g., '96k', '128k'. # Due to quality degraded too much, will temporary disabled this input
            scale_resolution (str): Optional. Resize video using format like '1280:720'. Set to None to keep original.
            metadata (bool): Keep metadata (True to keep previous video's metadata, False to let it be).

        Returns:
            str: Path to the optimized video.
        
        Raises:
            FileNotFoundError: If input file is missing.
            RuntimeError: If FFmpeg fails.
        """

        # CONSTANT
        CRF_264 = 23
        CRF_265 = 26

        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        base, ext = os.path.splitext(output_path or input_path)
        if output_path is None:
            output_path = f"{base}_optimized.mp4"

        if ext != ".mp4":
            output_path = f"{base}.mp4"

        if crf is None:
            crf = CRF_265 if codec == 'libx265' else CRF_264
        elif not (0 <= crf <= 51):
            raise ValueError("CRF must be an integer between 0 and 51.")

        # Get video duration for progress bar
        total_duration = self.get_video_duration(input_path)

        # Base ffmpeg command
        cmd = [
            self._ffmpeg,
            "-y",                    # Overwrite output
            "-i", input_path,        # Input file
            "-c:v", codec,           # Set Video quality
            "-preset", preset,       # processing efficency (the slower the better result)
            "-crf", str(crf),        # Set video frame rate
            "-map_metadata", "0",    # Keep original metadata
        ]

        # Optional resolution scaling
        if scale_resolution:
            cmd += ["-vf", f"scale={scale_resolution}"]

        # Audio re-encode
        cmd += [
            "-c:a", "copy",              # compress audio, remain audio quality
            # "-b:a", audio_bitrate,      # audio bitrate
        ]

        # Optimize for streaming
        if streaming:
            cmd += [
                "-movflags", "+faststart",  # Optimize for streaming
            ]
        
        # Set output location
        cmd.append(output_path)

        print()

        # Run FFmpeg and parse progress
        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            universal_newlines=True,
            bufsize=1
        )

        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+).(\d+)")
        pbar = tqdm(total=total_duration, unit="s", desc="Encoding")

        for line in process.stderr:
            match = time_pattern.search(line)
            if match:
                h, m, s, ms = map(int, match.groups())
                current_time = h * 3600 + m * 60 + s + ms / 100.0
                pbar.n = min(current_time, total_duration)
                pbar.refresh()

        process.wait()
        pbar.n = total_duration
        pbar.refresh()
        pbar.close()
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg failed:\n{line}")
        
        if metadata:
            self.replace_metadata(input_path, output_path)

        return output_path
    #endregion

    #region Get Version
    @property
    def get_exiftool_version(self):
        try:
            result = subprocess.run([self._exiftool, '-ver'], capture_output=True, text=True).stdout.strip()
            return (f"exiftool-{result}")
        except FileNotFoundError as e:
            raise e

    @staticmethod
    def extract_version(text: str):
        match = re.search(r'version\s+([\d.]+)', text)
        return match.group(1) if match else None

    @property
    def get_ffmpeg_version(self):
        try:
            result = subprocess.run([self._ffmpeg, '-version'], capture_output=True, text=True).stdout
            return (f"ffmpeg-{MediaOptimizer.extract_version(result)}")
        except FileNotFoundError as e:
            raise e

    @property
    def get_ffprobe_version(self):
        try:
            result = subprocess.run([self._ffprobe, '-version'], capture_output=True, text=True).stdout
            return (f"ffprobe-{MediaOptimizer.extract_version(result)}")
        except FileNotFoundError as e:
            raise e
    #endregion