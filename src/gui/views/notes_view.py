import os
import random
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSizePolicy, QScrollArea

from src.config import DATA_DIRECTORY
from src.gui.views.base_view import BaseView


class NotesView(BaseView):
    def __init__(self):
        super().__init__("Notes")
        self._setup_ui()
        self.load_notes()

    def _setup_ui(self):
        """
        Sets up the UI layout, ensuring content is centered.
        """
        main_layout = QVBoxLayout()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(35)
        content_layout.setAlignment(Qt.AlignCenter)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.notes_container_widget = QWidget()
        self.notes_container = QVBoxLayout(self.notes_container_widget)
        self.notes_container.setAlignment(Qt.AlignCenter)
        self.notes_container.setSpacing(20)

        self.scroll_area.setWidget(self.notes_container_widget)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(self.scroll_area)

        main_layout.addLayout(content_layout)
        self.layout.addLayout(main_layout)

    def load_notes(self):
        """
        Loads and displays notes from the data directory.
        """
        if not os.path.exists(DATA_DIRECTORY):
            return

        folders = [f for f in os.listdir(DATA_DIRECTORY) if os.path.isdir(os.path.join(DATA_DIRECTORY, f))]
        for folder in sorted(folders, reverse=True):
            formatted_date = self.format_folder_name(folder)
            screenshot_path = self.get_random_screenshot(os.path.join(DATA_DIRECTORY, folder, "screenshots"))

            if screenshot_path:
                self.add_note_widget(formatted_date, screenshot_path)

    def format_folder_name(self, folder_name):
        """
        Formats the folder name into a human-readable date.
        """
        try:
            dt = datetime.strptime(folder_name, "%Y-%m-%d_%H-%M-%S")
            return dt.strftime("%d %B %Y, %H:%M")
        except ValueError:
            return folder_name

    def get_random_screenshot(self, screenshots_dir):
        """
        Retrieves a random screenshot from the specified directory.
        """
        if not os.path.exists(screenshots_dir):
            return None

        screenshots = [f for f in os.listdir(screenshots_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not screenshots:
            return None

        return os.path.join(screenshots_dir, random.choice(screenshots))

    def add_note_widget(self, formatted_date, screenshot_path):
        """
        Creates and adds a note widget to the layout.
        """
        note_widget = QPushButton()
        note_widget.setStyleSheet(
            "border-radius: 10px; "
            "background-color: #444; "
            "padding: 10px; "
            "min-width: 500px; "
            "max-width: 500px; "
            "min-height: 120px; "
        )

        layout = QHBoxLayout()

        pixmap = QPixmap(screenshot_path)
        pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignLeft)

        date_label = QLabel(formatted_date)
        date_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        date_label.setFont(self.font())

        layout.addWidget(image_label)
        layout.addWidget(date_label)
        layout.addStretch()
        note_widget.setLayout(layout)

        note_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.notes_container.addWidget(note_widget, alignment=Qt.AlignCenter)
