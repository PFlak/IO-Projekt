from PySide6.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QLineEdit,
                               QFileDialog, QComboBox, QSpinBox, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy)

from src.config import settings, update_settings
from src.gui.views.base_view import BaseView
from src.utils.logger import app_logger


class SettingsView(BaseView):
    def __init__(self):
        super().__init__("Settings")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout()

        # Centering the content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(35)
        content_layout.setContentsMargins(100, 30, 100, 30)

        # Data Directory
        data_dir_layout = QVBoxLayout()
        data_dir_layout.setSpacing(10)
        data_dir_label = QLabel("Data Directory:")
        self.data_dir_input = QLineEdit(settings.get("data_directory", ""))
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._browse_data_directory)
        data_dir_input_layout = QHBoxLayout()
        data_dir_input_layout.addWidget(self.data_dir_input)
        data_dir_input_layout.addWidget(browse_button)
        data_dir_layout.addWidget(data_dir_label)
        data_dir_layout.addLayout(data_dir_input_layout)
        content_layout.addLayout(data_dir_layout)

        # Model Size
        model_layout = QVBoxLayout()
        model_layout.setSpacing(10)
        model_label = QLabel("Speech-to-Text Model Size (Larger models are slower but more accurate):")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large", "turbo"])
        self.model_combo.setCurrentText(settings.get("model_size", "small"))
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        content_layout.addLayout(model_layout)

        # Transcription Language
        language_layout = QVBoxLayout()
        language_layout.setSpacing(10)
        language_label = QLabel("Transcription Language:")
        self.language_combo = QComboBox()
        languages = {
            "en": "English", "zh": "Chinese", "de": "German", "es": "Spanish",
            "ko": "Korean", "fr": "French", "ja": "Japanese", "pl": "Polish",
            "pt": "Portuguese", "tr": "Turkish", "it": "Italian",
        }
        for code, name in languages.items():
            self.language_combo.addItem(name, code)
        self.language_combo.setCurrentText(languages.get(settings.get("transcription_language", "pl"), "Polish"))
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        content_layout.addLayout(language_layout)

        # Max Data Folder Size (in GB)
        max_size_layout = QVBoxLayout()
        max_size_layout.setSpacing(10)
        max_size_label = QLabel("Max Data Folder Size (GB):")
        self.max_size_spinbox = QSpinBox()
        self.max_size_spinbox.setRange(1, 100)
        self.max_size_spinbox.setValue(settings.get("max_data_size_gb", 5))
        max_size_layout.addWidget(max_size_label)
        max_size_layout.addWidget(self.max_size_spinbox)
        content_layout.addLayout(max_size_layout)

        # Save Button
        save_button = QPushButton("Save Settings")
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
        folder = QFileDialog.getExistingDirectory(self, "Select Data Directory")
        if folder:
            self.data_dir_input.setText(folder)

    def _save_settings(self):
        new_settings = {
            "data_directory": self.data_dir_input.text(),
            "model_size": self.model_combo.currentText(),
            "transcription_language": self.language_combo.currentData(),
            "max_data_size_gb": self.max_size_spinbox.value()
        }
        update_settings(new_settings)
        QMessageBox.information(self, "Success", "Settings have been saved.")
        app_logger.info("Settings updated: {}".format(new_settings))
