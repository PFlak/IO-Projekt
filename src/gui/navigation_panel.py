from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtGui import QIcon
from src.config import ICON_DIRECTORY
import os


class NavigationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        # Icons
        home_icon = os.path.join(ICON_DIRECTORY, 'home.svg')
        notes_icon = os.path.join(ICON_DIRECTORY, 'notes.svg')
        calendar_icon = os.path.join(ICON_DIRECTORY, 'calendar.svg')
        settings_icon = os.path.join(ICON_DIRECTORY, 'settings.svg')

        # Buttons
        self.main_button = self.create_button(home_icon)
        self.notes_button = self.create_button(notes_icon)
        self.calendar_button = self.create_button(calendar_icon)
        self.settings_button = self.create_button(settings_icon)

        # Add buttons to layout
        self.layout.addStretch()
        self.layout.addWidget(self.main_button)
        self.layout.addWidget(self.notes_button)
        self.layout.addWidget(self.calendar_button)
        self.layout.addWidget(self.settings_button)
        self.layout.addStretch()

    def create_button(self, icon_path):
        button = QPushButton()
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setMinimumSize(50, 50)
        button.setMaximumSize(50, 50)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(30, 30))
        return button
