import re
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QLineEdit,
                               QFileDialog, QComboBox, QSpinBox, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy)
from src.utils.languages import LANGUAGES

from src.config import settings, update_settings
from src.gui.views.base_view import BaseView
from src.utils.logger import app_logger


class SettingsView(BaseView):
    """
    A user interface view for managing application settings.

    The SettingsView provides input fields, dropdowns, and buttons for configuring various application settings,
    including data directory, maximum data folder size, calendar URL, speech-to-text model size, and transcription language.

    Inherits from `BaseView`.

    Attributes
    ----------
    data_dir_input : QLineEdit
        Input field for specifying the data directory path.
    max_size_spinbox : QSpinBox
        Spin box for selecting the maximum size of the data directory (in GB).
    calendar_url_input : QLineEdit
        Input field for specifying the Google Calendar URL.
    model_combo : QComboBox
        Dropdown for selecting the speech-to-text model size.
    language_combo : QComboBox
        Dropdown for selecting the transcription language.

    Methods
    -------
    _setup_ui()
        Sets up the user interface components for the view.
    _browse_data_directory()
        Opens a file dialog to browse and select the data directory.
    _validate_calendar_url(url)
        Validates the provided Google Calendar URL format.
    _save_settings()
        Saves the updated settings and restarts the application.
    _restart_application()
        Restarts the application after saving settings.
    """

    def __init__(self):
        """
        Initializes the SettingsView instance.

        Sets the title of the view to "Settings" and configures the user interface by calling `_setup_ui`.
        """
        super().__init__("Settings")
        self._setup_ui()

    def _setup_ui(self):
        """
        Configures the user interface components for the settings view.

        Includes fields and buttons for setting data directory, maximum folder size, calendar URL,
        speech-to-text model size, and transcription language. A save button is also provided to
        save the changes and restart the application.
        """
        main_layout = QVBoxLayout()

        # Centering the content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(35)
        content_layout.setAlignment(Qt.AlignCenter)

        input_width = 600

        # Data Directory
        data_dir_layout = QVBoxLayout()
        data_dir_layout.setSpacing(10)
        data_dir_label = QLabel("Data Directory:")
        self.data_dir_input = QLineEdit(settings.get("data_directory", ""))
        self.data_dir_input.setFixedWidth(input_width - 100)
        browse_button = QPushButton("Browse")
        browse_button.setFixedWidth(100)
        browse_button.clicked.connect(self._browse_data_directory)
        data_dir_input_layout = QHBoxLayout()
        data_dir_input_layout.addWidget(self.data_dir_input)
        data_dir_input_layout.addWidget(browse_button)
        data_dir_layout.addWidget(data_dir_label)
        data_dir_layout.addLayout(data_dir_input_layout)
        content_layout.addLayout(data_dir_layout)

        # Max Data Folder Size (in GB)
        max_size_layout = QVBoxLayout()
        max_size_layout.setSpacing(10)
        max_size_label = QLabel("Max Data Folder Size (GB):")
        self.max_size_spinbox = QSpinBox()
        self.max_size_spinbox.setRange(1, 100)
        self.max_size_spinbox.setValue(settings.get("max_data_size_gb", 5))
        self.max_size_spinbox.setFixedWidth(input_width)
        max_size_layout.addWidget(max_size_label)
        max_size_layout.addWidget(self.max_size_spinbox)
        content_layout.addLayout(max_size_layout)

        # Calendar URL
        calendar_url_layout = QVBoxLayout()
        calendar_url_layout.setSpacing(10)
        calendar_url_label = QLabel("Google Calendar URL (make sure it is set to public for proper display):")
        self.calendar_url_input = QLineEdit(settings.get("calendar_url", ""))
        self.calendar_url_input.setFixedWidth(input_width)
        calendar_url_layout.addWidget(calendar_url_label)
        calendar_url_layout.addWidget(self.calendar_url_input)
        content_layout.addLayout(calendar_url_layout)

        # Model Size
        model_layout = QVBoxLayout()
        model_layout.setSpacing(10)
        model_label = QLabel("Speech-to-Text Model Size (larger models are slower but more accurate):")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large", "turbo"])
        self.model_combo.setCurrentText(settings.get("model_size", "small"))
        self.model_combo.setFixedWidth(input_width)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        content_layout.addLayout(model_layout)

        # Transcription Language
        language_layout = QVBoxLayout()
        language_layout.setSpacing(10)
        language_label = QLabel("Transcription Language:")
        self.language_combo = QComboBox()
        for code, name in sorted(LANGUAGES.items(), key=lambda item: item[1]):
            self.language_combo.addItem(name, code)
        self.language_combo.setCurrentText(LANGUAGES.get(settings.get("transcription_language", "pl"), "Polish"))
        self.language_combo.setFixedWidth(input_width)
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        content_layout.addLayout(language_layout)

        # OpenAI API Key
        api_key_layout = QVBoxLayout()
        api_key_layout.setSpacing(10)
        api_key_label = QLabel("OpenAI API Key:")
        self.api_key_input = QLineEdit(settings.get("open_ai_api_key", ""))
        self.api_key_input.setFixedWidth(input_width)
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        content_layout.addLayout(api_key_layout)

        # Save Button
        save_button = QPushButton("Save Settings and Restart Application")
        save_button.setFixedWidth(input_width)
        save_button.clicked.connect(self._save_settings)
        content_layout.addWidget(save_button)

        # Center alignment
        spacer_top = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacer_bottom = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer_top)
        main_layout.addLayout(content_layout)
        main_layout.addItem(spacer_bottom)

        self.layout.addLayout(main_layout)

    def _browse_data_directory(self):
        """
        Opens a file dialog to select a data directory.

        Updates the data directory input field with the selected path.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if folder:
            self.data_dir_input.setText(folder)

    def _validate_calendar_url(self, url):
        """
        Validates the provided Google Calendar URL format.

        :param url: The Google Calendar URL to validate.
        :type url: str
        :return: True if the URL is valid or empty; False otherwise.
        :rtype: bool
        """
        if not url:
            return True
        pattern = r'^https:\/\/calendar\.google\.com\/calendar\/embed\?.+'
        return re.match(pattern, url) is not None

    def _validate_api_key(self, key):
        return bool(re.fullmatch(r'^[a-zA-Z0-9-_]+$', key))

    def _save_settings(self):
        """
        Saves the current settings and restarts the application.

        Validates the Google Calendar URL, updates the settings, and initiates a restart if valid.
        """
        calendar_url = self.calendar_url_input.text().strip()
        if not self._validate_calendar_url(calendar_url):
            QMessageBox.warning(self, "Invalid URL", "Please provide a valid Google Calendar URL.")
            app_logger.warning("Invalid Google Calendar URL provided.")
            return

        api_key = self.api_key_input.text().strip()
        if not self._validate_api_key(api_key):
            QMessageBox.warning(self, "Invalid API Key", "Please provide a valid OpenAI API key.")
            app_logger.warning("Invalid OpenAI API Key provided.")
            return

        new_settings = {
            "data_directory": self.data_dir_input.text(),
            "max_data_size_gb": self.max_size_spinbox.value(),
            "model_size": self.model_combo.currentText(),
            "transcription_language": self.language_combo.currentData(),
            "calendar_url": self.calendar_url_input.text(),
            "open_ai_api_key": self.api_key_input.text().strip(),
        }
        update_settings(new_settings)
        QMessageBox.information(self, "Success", "Settings have been saved. The app will now restart.")
        app_logger.info("Settings updated")

        self._restart_application()

    def _restart_application(self):
        """
        Restarts the application after saving settings.
        """
        app_logger.info("Restarting application...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
