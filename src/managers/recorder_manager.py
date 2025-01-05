import os
import threading
import time
from datetime import datetime

from pygetwindow import getWindowsWithTitle

from src.config import DATA_DIRECTORY
from src.services.audio_recorder import AudioRecorder
from src.services.screenshot_taker import ScreenshotTaker
from src.services.video_recorder import VideoRecorder
from src.utils.logger import app_logger


class RecorderManager:
    def __init__(self, window_title):
        self.window_title = window_title
        self.is_recording = False
        self.session_dir = None
        self.audio_recorder = None
        self.video_recorder = None
        self.screenshot_taker = None

    def _create_session_directory(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = os.path.join(DATA_DIRECTORY, timestamp)
        os.makedirs(self.session_dir, exist_ok=True)
        app_logger.info(f"Session directory created at {self.session_dir}.")

    def start_recording(self):
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

        app_logger.info("Recording stopped.")

    def monitor_window(self):
        while self.is_recording:
            try:
                getWindowsWithTitle(self.window_title)[0]
            except IndexError:
                app_logger.warning("Target window closed. Stopping recording.")
                self.stop_recording()
            time.sleep(1)
