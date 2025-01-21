from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtGui import QIcon
from src.config import ICON_DIRECTORY
import os


class NavigationPanel(QWidget):
    """
    A custom navigation panel widget with buttons for different sections of an application.

    This panel provides navigation buttons with icons for "Home," "Notes," "Calendar,"
    and "Settings." The layout is a vertical box layout (`QVBoxLayout`) that ensures
    the buttons are spaced evenly.

    Inherits from `QWidget`.

    Attributes
    ----------
    layout : QVBoxLayout
        The main layout of the panel, arranging buttons vertically.
    main_button : QPushButton
        Button for navigating to the "Home" section.
    notes_button : QPushButton
        Button for navigating to the "Notes" section.
    calendar_button : QPushButton
        Button for navigating to the "Calendar" section.
    settings_button : QPushButton
        Button for navigating to the "Settings" section.

    Methods
    -------
    create_button(icon_path)
        Creates a QPushButton with a specified icon.
    """

    def __init__(self, parent=None):
        """
        Initializes the NavigationPanel widget.

        :param parent: The parent widget of this panel. Defaults to None.
        :type parent: QWidget, optional
        """
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
        """
        Creates a QPushButton with the specified icon.

        The button has fixed dimensions of 50x50 pixels and displays the icon
        with a size of 30x30 pixels.

        :param icon_path: The path to the icon image for the button.
        :type icon_path: str
        :return: A QPushButton instance configured with the specified icon.
        :rtype: QPushButton
        """
        button = QPushButton()
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setMinimumSize(50, 50)
        button.setMaximumSize(50, 50)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(30, 30))
        return button
