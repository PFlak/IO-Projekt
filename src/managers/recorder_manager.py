import os
import threading
import time
from datetime import datetime

from pygetwindow import getWindowsWithTitle

from src.config import DATA_DIRECTORY
from src.services.audio_recorder import AudioRecorder
from src.services.merge_media import MergeMedia
from src.services.screenshot_taker import ScreenshotTaker
from src.services.video_recorder import VideoRecorder
from src.utils.logger import app_logger


class RecorderManager:
    """
    Manages audio, video, and screenshot recording for a specified window.

    This class combines functionalities from the `AudioRecorder`, `VideoRecorder`, and
    `ScreenshotTaker` classes to simultaneously record audio, video, and periodic screenshots
    of a specified application window.

    Attributes
    ----------
    window_title : str
        The title of the target window to record.
    is_recording : bool
        Indicates whether the recording process is active.
    session_dir : str or None
        The directory where session data (audio, video, screenshots) is saved.
    audio_recorder : AudioRecorder or None
        The `AudioRecorder` instance for capturing audio.
    video_recorder : VideoRecorder or None
        The `VideoRecorder` instance for capturing video.
    screenshot_taker : ScreenshotTaker or None
        The `ScreenshotTaker` instance for capturing screenshots.

    Methods
    -------
    start_recording()
        Starts audio, video, and screenshot recording for the target window.
    stop_recording()
        Stops all active recording processes.
    monitor_window()
        Monitors the target window and stops recording if the window is closed.
    """

    def __init__(self, window_title):
        """
        Initializes the RecorderManager class.

        :param window_title: The title of the target window to record.
        :type window_title: str
        """
        self.window_title = window_title
        self.is_recording = False
        self.session_dir = None
        self.audio_recorder = None
        self.video_recorder = None
        self.screenshot_taker = None

    def _create_session_directory(self):
        """
        Creates a session directory to store the recorded data.

        The directory is named with the current timestamp and is created in the global
        `DATA_DIRECTORY`.

        :raises OSError: If the session directory cannot be created.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = os.path.join(DATA_DIRECTORY, timestamp)
        os.makedirs(self.session_dir, exist_ok=True)
        app_logger.info(f"Session directory created at {self.session_dir}.")

    def start_recording(self):
        """
        Starts recording audio, video, and screenshots for the target window.

        Initializes the `AudioRecorder`, `VideoRecorder`, and `ScreenshotTaker` classes and
        starts their recording processes in separate threads.

        :raises Exception: If an error occurs while starting the recording process.
        """
        if self.is_recording:
            app_logger.warning("Recording is already in progress.")
            return

        try:
            self._create_session_directory()
            self.audio_recorder = AudioRecorder(self.session_dir)
            self.video_recorder = VideoRecorder(self.session_dir, self.window_title)
            self.screenshot_taker = ScreenshotTaker(self.session_dir, self.window_title)

            self.is_recording = True

            self.audio_thread = threading.Thread(target=self.audio_recorder.start_recording)
            self.video_thread = threading.Thread(target=self.video_recorder.start_recording)
            self.screenshot_thread = threading.Thread(target=self.screenshot_taker.start_screenshots)

            self.audio_thread.start()
            self.video_thread.start()
            self.screenshot_thread.start()

            app_logger.info("Recording started.")
        except Exception as e:
            app_logger.error(f"Failed to start recording: {e}")
            self.stop_recording()

    def stop_recording(self):
        """
        Stops all recording processes (audio, video, and screenshots).

        Ensures all threads are joined and all resources are released.
        """
        if not self.is_recording:
            app_logger.warning("No recording is in progress to stop.")
            return

        self.is_recording = False

        if self.audio_recorder:
            self.audio_recorder.stop_recording()
        if self.video_recorder:
            self.video_recorder.stop_recording()
        if self.screenshot_taker:
            self.screenshot_taker.stop_screenshots()

        if hasattr(self, 'audio_thread') and self.audio_thread:
            self.audio_thread.join()
        if hasattr(self, 'video_thread') and self.video_thread:
            self.video_thread.join()
        if hasattr(self, 'screenshot_thread') and self.screenshot_thread:
            self.screenshot_thread.join()

        merger = MergeMedia(self.session_dir)
        merger.merge_audio_video()

        app_logger.info("Recording stopped.")

    def monitor_window(self):
        """
        Monitors the target window and stops recording if the window is closed.

        This method should be run in a separate thread to continuously check the availability
        of the target window.

        :raises RuntimeError: If the window is closed during recording.
        """
        while self.is_recording:
            try:
                getWindowsWithTitle(self.window_title)[0]
            except IndexError:
                app_logger.warning("Target window closed. Stopping recording.")
                self.stop_recording()
            time.sleep(1)
