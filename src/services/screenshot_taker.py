import os
import time
from datetime import datetime

from PIL import Image
from mss import mss
from pygetwindow import getWindowsWithTitle

from src.utils.logger import app_logger


class ScreenshotTaker:
    """
    A class for periodically taking screenshots of a specific application window.

    Screenshots are saved to a directory in a timestamped format.

    Attributes
    ----------
    session_dir : str
        The directory where screenshots will be saved.
    window_title : str
        The title of the application window to capture screenshots from.
    interval : int
        The time interval (in seconds) between consecutive screenshots.
    is_running : bool
        Indicates whether the screenshot capture process is running.
    window_rect : dict or None
        The dimensions and position of the application window being captured.

    Methods
    -------
    start_screenshots()
        Starts capturing screenshots of the specified application window.
    stop_screenshots()
        Stops the screenshot capture process.
    """
    def __init__(self, session_dir, window_title):
        """
        Initializes the ScreenshotTaker class.

        :param session_dir: The directory where screenshots will be saved.
        :type session_dir: str
        :param window_title: The title of the application window to capture screenshots from.
        :type window_title: str
        """
        self.window_rect = None
        self.session_dir = os.path.join(session_dir, "screenshots")
        os.makedirs(self.session_dir, exist_ok=True)
        self.window_title = window_title
        self.interval = 10
        self.is_running = False

    def _get_window_rect(self):
        """
        Retrieves the dimensions and position of the specified application window.

        :returns: A dictionary containing the keys 'left', 'top', 'width', and 'height' for the window's dimensions.
        :rtype: dict

        :raises ValueError: If no window with the specified title is found.
        """
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
        """
        Starts capturing screenshots of the specified application window.

        Captures screenshots at regular intervals defined by the `interval` attribute and saves them
        as PNG files in the session directory.

        :raises Exception: If an error occurs during the screenshot capture process, it will be logged.
        """
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
        """
        Stops the screenshot capture process.

        Updates the `is_running` attribute to stop capturing screenshots.
        """
        self.is_running = False
        app_logger.info("Screenshot capture stopped.")
