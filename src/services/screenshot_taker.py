import os
import time
from datetime import datetime

from PIL import Image
from mss import mss
from pygetwindow import getWindowsWithTitle

from src.utils.logger import app_logger


class ScreenshotTaker:
    def __init__(self, session_dir, window_title):
        self.window_rect = None
        self.session_dir = os.path.join(session_dir, "screenshots")
        os.makedirs(self.session_dir, exist_ok=True)
        self.window_title = window_title
        self.interval = 10
        self.is_running = False

    def _get_window_rect(self):
        windows = getWindowsWithTitle(self.window_title)
        if not windows:
            raise ValueError(f"Window with title '{self.window_title}' not found.")

        window = windows[0]
        return {
            'left': window.left,
            'top': window.top,
            'width': window.width,
            'height': window.height
        }

    def start_screenshots(self):
        try:
            app_logger.info("Starting screenshot capture.")
            self.is_running = True
            self.window_rect = self._get_window_rect()

            with mss() as sct:
                while self.is_running:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    screenshot_path = os.path.join(self.session_dir, f"screenshot_{timestamp}.png")
                    screenshot = sct.grab(self.window_rect)

                    # Save screenshot using Pillow
                    image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                    image.save(screenshot_path)

                    time.sleep(self.interval)
        except Exception as e:
            app_logger.error(f"Screenshot capture error: {e}")

    def stop_screenshots(self):
        self.is_running = False
        app_logger.info("Screenshot capture stopped.")
