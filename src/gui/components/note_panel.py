import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QTextCharFormat, QTextCursor, QBrush, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QWidget, QPushButton, QHBoxLayout, QStackedWidget, QTextEdit,
    QLineEdit, QSlider, QSizePolicy
)

from src.config import DATA_DIRECTORY


class NotePanel(QWidget):
    """
    A panel for displaying details of a selected note folder, allowing navigation between different content types.

    Displays:
    - Screenshots (navigable with left/right arrows)
    - Transcription text with search functionality
    - Summary notes with search functionality
    - Video recording playback
    """

    def __init__(self, folder_name: str, return_callback):
        """
        Initializes the NotePanel instance and sets up the UI.

        :param folder_name: The name of the selected folder to display.
        :param return_callback: Function to call when returning to NotesView.
        """
        super().__init__()
        self.folder_name = folder_name
        self.return_callback = return_callback
        self.screenshots = []
        self.current_screenshot_index = 0
        self._setup_ui()
        self.load_content()

    def _setup_ui(self):
        """Creates and configures UI components for the panel."""
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # Stacked widget for different views
        self.content_stack = QStackedWidget()

        # Screenshots Viewer
        self.screenshot_label = QLabel("No screenshots available")
        self.screenshot_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_prev_button = QPushButton("←")
        self.screenshot_prev_button.setFixedSize(40, 200)
        self.screenshot_next_button = QPushButton("→")
        self.screenshot_next_button.setFixedSize(40, 200)
        self.screenshot_prev_button.clicked.connect(self.show_previous_screenshot)
        self.screenshot_next_button.clicked.connect(self.show_next_screenshot)
        screenshot_nav_layout = QHBoxLayout()
        screenshot_nav_layout.addWidget(self.screenshot_prev_button)
        screenshot_nav_layout.addWidget(self.screenshot_label)
        screenshot_nav_layout.addWidget(self.screenshot_next_button)
        screenshot_widget = QWidget()
        screenshot_widget.setLayout(screenshot_nav_layout)
        self.content_stack.addWidget(screenshot_widget)

        # Transcription Viewer
        self.transcription_search = QLineEdit()
        self.transcription_search.setPlaceholderText("Search transcription...")
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(True)
        self.transcription_search.textChanged.connect(self.search_transcription)
        transcription_layout = QVBoxLayout()
        transcription_layout.addWidget(self.transcription_search)
        transcription_layout.addWidget(self.transcription_text)
        transcription_widget = QWidget()
        transcription_widget.setLayout(transcription_layout)
        self.content_stack.addWidget(transcription_widget)

        # Summary Viewer
        self.summary_search = QLineEdit()
        self.summary_search.setPlaceholderText("Search summary...")
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_search.textChanged.connect(self.search_summary)
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(self.summary_search)
        summary_layout.addWidget(self.summary_text)
        summary_widget = QWidget()
        summary_widget.setLayout(summary_layout)
        self.content_stack.addWidget(summary_widget)

        # Video Player
        self.video_widget = QVideoWidget()
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_video_position)
        self.status_label = QLabel("00:00 / 00:00")
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.setVideoOutput(self.video_widget)
        video_layout = QVBoxLayout()
        video_layout.addWidget(self.video_widget)
        video_widget = QWidget()
        video_widget.setLayout(video_layout)
        self.content_stack.addWidget(video_widget)
        self.video_controls_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.play_button.clicked.connect(self.media_player.play)
        self.pause_button.clicked.connect(self.media_player.pause)
        self.video_controls_layout.addWidget(self.play_button)
        self.video_controls_layout.addWidget(self.pause_button)
        self.video_controls_layout.addWidget(self.position_slider)
        self.video_controls_layout.addWidget(self.status_label)
        self.video_controls_layout.addWidget(self.pause_button)
        video_layout.addLayout(self.video_controls_layout)

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        self.screenshots_button = QPushButton("Screenshots")
        self.transcription_button = QPushButton("Transcription")
        self.summary_button = QPushButton("Summary")
        self.video_button = QPushButton("Video")
        self.return_button = QPushButton("Back")
        self.screenshots_button.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.transcription_button.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.summary_button.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
        self.video_button.clicked.connect(lambda: self.content_stack.setCurrentIndex(3))
        self.return_button.clicked.connect(self.return_callback)
        nav_layout.addWidget(self.screenshots_button)
        nav_layout.addWidget(self.transcription_button)
        nav_layout.addWidget(self.summary_button)
        nav_layout.addWidget(self.video_button)
        nav_layout.addWidget(self.return_button)

        self.layout.addWidget(self.content_stack)
        self.layout.addLayout(nav_layout)
        self.setLayout(self.layout)

    def update_position(self, position):
        """Updates the position slider and status label."""
        self.position_slider.setValue(position)
        duration = self.media_player.duration()
        if duration > 0:
            self.status_label.setText(
                f"{position // 60000:02}:{(position // 1000) % 60:02} / {duration // 60000:02}:{(duration // 1000) % 60:02}"
            )

    def update_duration(self, duration):
        """Sets the range for the position slider based on duration."""
        self.position_slider.setRange(0, duration)

    def set_video_position(self, position):
        """Sets the media player's position."""
        self.media_player.setPosition(position)

    def load_content(self):
        """Loads content from the selected folder."""
        folder_path = os.path.join(DATA_DIRECTORY, self.folder_name)
        screenshots_dir = os.path.join(folder_path, "screenshots")
        transcription_file = os.path.join(folder_path, "transcription.txt")
        summary_file = os.path.join(folder_path, "summarize.md")
        video_file = os.path.join(folder_path, "video.mp4")

        if os.path.exists(screenshots_dir):
            self.screenshots = [
                os.path.join(screenshots_dir, f)
                for f in os.listdir(screenshots_dir)
                if f.endswith((".png", ".jpg", ".jpeg"))
            ]
            self.show_screenshot()

        if os.path.exists(transcription_file):
            with open(transcription_file, "r", encoding="utf-8") as file:
                self.transcription_text.setText(file.read())

        if os.path.exists(summary_file):
            with open(summary_file, "r", encoding="utf-8") as file:
                self.summary_text.setText(file.read())

        if os.path.exists(video_file):
            self.media_player.setSource(QUrl.fromLocalFile(video_file))

    def adjust_screenshot_size(self):
        """Adjusts the screenshot size to maintain aspect ratio."""
        if self.screenshots:
            pixmap = QPixmap(self.screenshots[self.current_screenshot_index])
            scaled_pixmap = pixmap.scaled(
                self.width() * 0.9,
                self.height() * 0.9,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.screenshot_label.setPixmap(scaled_pixmap)

    def show_screenshot(self):
        """Displays the current screenshot."""
        self.adjust_screenshot_size()

    def show_previous_screenshot(self):
        """Navigates to the previous screenshot."""
        if self.screenshots:
            self.current_screenshot_index = (self.current_screenshot_index - 1) % len(self.screenshots)
            self.show_screenshot()

    def show_next_screenshot(self):
        """Navigates to the next screenshot."""
        if self.screenshots:
            self.current_screenshot_index = (self.current_screenshot_index + 1) % len(self.screenshots)
            self.show_screenshot()

    def highlight_search_results(self, text_edit, query):
        """Highlights all occurrences of the search term in the given QTextEdit widget."""
        text_edit.moveCursor(QTextCursor.Start)

        # Clear previous highlights
        fmt_clear = QTextCharFormat()
        text_edit.setExtraSelections([])

        if not query:
            return

        # Highlight new occurrences
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QBrush(QColor("yellow")))
        highlight_format.setForeground(QBrush(QColor("black")))

        selections = []
        cursor = text_edit.textCursor()
        document = text_edit.document()

        cursor = document.find(query, cursor)
        while not cursor.isNull():
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = highlight_format
            selections.append(selection)
            cursor = document.find(query, cursor)

        text_edit.setExtraSelections(selections)

    def search_transcription(self, text):
        """Searches and highlights text in the transcription view."""
        self.highlight_search_results(self.transcription_text, text)

    def search_summary(self, text):
        """Searches and highlights text in the summary view."""
        self.highlight_search_results(self.summary_text, text)

    def resizeEvent(self, event):
        """Handles window resizing to adjust screenshot size."""
        super().resizeEvent(event)
        self.adjust_screenshot_size()
