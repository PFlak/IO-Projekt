from PySide6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QMessageBox
from PySide6.QtCore import Qt, QTimer
from pygetwindow import getAllTitles
from src.managers.recorder_manager import RecorderManager


class RecordingPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.recorder_manager = None
        self.is_recording = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.monitor_window)
        self.window_refresh_timer = QTimer()
        self.window_refresh_timer.timeout.connect(self.refresh_window_list)
        self.elapsed_time = 0
        self._setup_ui()
        self.window_refresh_timer.start(5000)

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.window_selector = QComboBox()
        self.window_selector.addItems(self.get_window_titles())
        self.window_selector.setFixedWidth(300)
        layout.addWidget(QLabel("Select Window to Record:"), alignment=Qt.AlignCenter)
        layout.addWidget(self.window_selector, alignment=Qt.AlignCenter)

        self.record_button = QPushButton("Start Recording")
        self.record_button.setFixedWidth(300)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button, alignment=Qt.AlignCenter)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.hide()
        layout.addWidget(self.timer_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def get_window_titles(self):
        return sorted([title for title in getAllTitles() if title.strip()])

    def refresh_window_list(self):
        current_selection = self.window_selector.currentText()
        self.window_selector.clear()
        self.window_selector.addItems(self.get_window_titles())
        index = self.window_selector.findText(current_selection)
        if index >= 0:
            self.window_selector.setCurrentIndex(index)

    def toggle_recording(self):
        selected_window = self.window_selector.currentText()
        if not self.is_recording:
            self.recorder_manager = RecorderManager(selected_window)
            self.recorder_manager.start_recording()
            self.is_recording = True
            self.record_button.setText("Stop Recording")
            self.timer_label.show()
            self.timer.start(1000)
            self.monitor_timer.start(1000)
        else:
            self.stop_recording()

    def stop_recording(self):
        if self.recorder_manager:
            self.recorder_manager.stop_recording()
        self.is_recording = False
        self.record_button.setText("Start Recording")
        self.timer_label.hide()
        self.timer.stop()
        self.monitor_timer.stop()
        self.elapsed_time = 0
        self.timer_label.setText("00:00:00")

    def update_timer(self):
        self.elapsed_time += 1
        hours, remainder = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def monitor_window(self):
        if self.recorder_manager and not any(
                self.recorder_manager.window_title in title for title in self.get_window_titles()):
            self.stop_recording()
            QMessageBox.warning(self, "Window Closed", "The recorded window has been closed. Recording will stop.")
