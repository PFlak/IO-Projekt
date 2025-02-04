from PySide6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QMessageBox, QLineEdit
from PySide6.QtCore import Qt, QTimer
from src.managers.recorder_manager import RecorderManager
from src.utils.visible_windows import get_visible_window_titles


class RecordingPanel(QWidget):
    """
    A panel to manage window recording, including selecting a window to record,
    starting and stopping recording, and displaying elapsed time.

    This class allows users to select a window to record, toggle recording on or off,
    and view the elapsed time during the recording. It monitors the selected window
    to stop recording if the window is closed.

    Inherits from `QWidget`.

    Attributes
    ----------
    recorder_manager : RecorderManager or None
        The manager responsible for controlling the recording process.
    is_recording : bool
        Indicates whether recording is currently active.
    timer : QTimer
        Timer used to update the elapsed time during recording.
    monitor_timer : QTimer
        Timer used to check if the selected window is still open.
    window_refresh_timer : QTimer
        Timer used to refresh the list of available windows periodically.
    elapsed_time : int
        The elapsed time in seconds for the current recording.
    window_selector : QComboBox
        Dropdown menu to select the window to record from a list of open windows.
    record_button : QPushButton
        Button to toggle the recording state between "Start Recording" and "Stop Recording".
    timer_label : QLabel
        Label displaying the elapsed recording time.

    Methods
    -------
    _setup_ui()
        Configures the user interface elements such as the window selector, record button, and timer.
    get_window_titles()
        Returns a sorted list of all open window titles to populate the window selector.
    refresh_window_list()
        Refreshes the list of available windows in the window selector.
    toggle_recording()
        Starts or stops recording based on the current recording state.
    stop_recording()
        Stops the recording, resets the state, and hides the timer.
    update_timer()
        Updates the displayed elapsed time during recording.
    monitor_window()
        Monitors if the selected window is still open; stops recording if the window is closed.
    """

    def __init__(self):
        """
        Initializes the RecordingPanel instance.

        Sets up the UI, initializes the recording-related timers, and starts the window list refresh timer.
        """
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
        """
        Configures the user interface for the RecordingPanel.

        Adds widgets such as a window selector, record button, and timer label to the layout.
        The layout is set to be centered and properly spaced.
        """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Regular Meeting")
        self.title_input.setFixedWidth(300)
        layout.addWidget(QLabel("Meeting Title"), alignment=Qt.AlignCenter)
        layout.addWidget(self.title_input, alignment=Qt.AlignCenter)

        self.window_selector = QComboBox()
        self.window_selector.addItems(self.get_window_titles())
        self.window_selector.setFixedWidth(300)
        self.window_selector.setMaxVisibleItems(10)
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
        """
        Retrieves the titles of all currently visible windows.

        Returns
        -------
        list of str
            Sorted list of visible window titles.
        """
        return get_visible_window_titles()

    def refresh_window_list(self):
        """
        Refreshes the list of available windows in the window selector.

        Retains the current window selection after refreshing the list.
        """
        current_selection = self.window_selector.currentText()
        self.window_selector.clear()
        self.window_selector.addItems(self.get_window_titles())
        index = self.window_selector.findText(current_selection)
        if index >= 0:
            self.window_selector.setCurrentIndex(index)

    def toggle_recording(self):
        """
        Toggles the recording state between starting and stopping the recording.

        Starts recording if not currently recording, and stops recording if it is.
        """
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
        """
        Stops the recording, resets the state, and hides the timer.

        Resets all the relevant UI elements, including stopping the recording timer.
        """
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
        """
        Updates the displayed elapsed time in the format HH:MM:SS.

        Increments the elapsed time by one second and updates the timer label accordingly.
        """
        self.elapsed_time += 1
        hours, remainder = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def monitor_window(self):
        """
        Monitors the selected window to check if it is still open.

        Stops the recording and shows a warning message if the selected window is closed.
        """
        if self.recorder_manager and not any(
                self.recorder_manager.window_title in title for title in self.get_window_titles()):
            self.stop_recording()
            QMessageBox.warning(self, "Window Closed", "The recorded window has been closed. Recording will stop.")
