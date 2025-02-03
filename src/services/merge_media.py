import subprocess
import os
from src.utils.logger import app_logger


class MergeMedia:
    """
    Handles merging an audio file with a video file.
    """

    def __init__(self, session_dir, video_filename="video.mp4", audio_filename="audio.wav"):
        """
        Initializes MergeMedia with session directory and file names.

        :param session_dir: Path to the directory containing video and audio files.
        :param video_filename: Name of the video file (default: "video.mp4").
        :param audio_filename: Name of the audio file (default: "audio.wav").
        """
        self.session_dir = session_dir
        self.video_file = os.path.join(session_dir, video_filename)
        self.audio_file = os.path.join(session_dir, audio_filename)
        self.temp_file = os.path.join(session_dir, "temp.mp4")

    def merge_audio_video(self):
        """
        Merges audio with video and overwrites the original video file.
        """
        if not os.path.exists(self.video_file) or not os.path.exists(self.audio_file):
            app_logger.error("Missing video or audio file.")
            return False

        command = [
            "ffmpeg", "-y",
            "-i", self.video_file,
            "-i", self.audio_file,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-strict", "experimental",
            self.temp_file
        ]

        try:
            subprocess.run(command, check=True)
            os.replace(self.temp_file, self.video_file)
            app_logger.info(f"Audio successfully added to {self.video_file}")
            return True
        except subprocess.CalledProcessError as e:
            app_logger.error(f"Failed to merge audio and video: {e}")
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
            return False
