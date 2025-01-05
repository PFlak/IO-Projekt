import os
import time

import cv2
import numpy as np
from mss import mss
from pygetwindow import getWindowsWithTitle

from src.utils.logger import app_logger


class VideoRecorder:
    def __init__(self, session_dir, window_title):
        self.session_dir = session_dir
        self.window_title = window_title
        self.is_recording = False
        self.video_writer = None
        self.window_rect = None

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

    def start_recording(self):
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
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
        app_logger.info("Video recording stopped.")
