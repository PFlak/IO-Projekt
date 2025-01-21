import os
import time

import cv2
import numpy as np
from mss import mss
from pygetwindow import getWindowsWithTitle

from src.utils.logger import app_logger


class VideoRecorder:
    """
    A class for recording videos of a specific application window.

    :param session_dir: The directory where the recorded video will be saved.
    :type session_dir: str
    :param window_title: The title of the application window to record.
    :type window_title: str
    """
    def __init__(self, session_dir, window_title):
        """
        Initializes the VideoRecorder class.

        :param session_dir: The directory where the recorded video will be saved.
        :type session_dir: str
        :param window_title: The title of the application window to record.
        :type window_title: str
        """
        self.session_dir = session_dir
        self.window_title = window_title
        self.is_recording = False
        self.video_writer = None
        self.window_rect = None

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

    def start_recording(self):
        """
        Starts recording the specified application window.

        Captures the application window's content and saves it as a video file in the session directory.

        :raises Exception: If an error occurs during the recording process, the recording will stop, and the exception is logged.
        """
        try:
            app_logger.info("Starting video recording.")
            self.window_rect = self._get_window_rect()
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            video_path = os.path.join(self.session_dir, "video.avi")

            self.video_writer = cv2.VideoWriter(
                video_path, fourcc, 20.0,
                (self.window_rect['width'], self.window_rect['height'])
            )

            self.is_recording = True
            target_fps = 20
            frame_duration = 1.0 / target_fps

            with mss() as sct:
                last_frame_time = time.time()
                while self.is_recording:
                    current_time = time.time()
                    elapsed_time = current_time - last_frame_time

                    if elapsed_time >= frame_duration:
                        frame = np.array(sct.grab(self.window_rect))
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        self.video_writer.write(frame)
                        last_frame_time = current_time

            self.video_writer.release()
        except Exception as e:
            app_logger.error(f"Video recording error: {e}")
            self.stop_recording()

    def stop_recording(self):
        """
        Stops the recording process and releases resources.

        Ensures the video writer is properly released and updates the recording status.
        """
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
        app_logger.info("Video recording stopped.")
