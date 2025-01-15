from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QSizePolicy

from src.config import settings, update_settings
from src.gui.views.base_view import BaseView
from src.utils.logger import app_logger


class CalendarView(BaseView):
    def __init__(self):
        super().__init__("Google Calendar")
        self.iframe_code = settings.get('iframe_code', '')
        self._setup_ui()

    def _setup_ui(self):
        self.input_layout = QVBoxLayout()

        instruction_label = QLabel("Make sure your Google Calendar is set to public for proper display.")
        self.layout.addWidget(instruction_label)

        self.iframe_input = QLineEdit()
        self.iframe_input.setPlaceholderText("Paste the Google Calendar iframe code here")
        self.iframe_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_layout.addWidget(self.iframe_input)

        self.save_button = QPushButton("Save")
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.save_button.clicked.connect(self._save_calendar_iframe)
        self.input_layout.addWidget(self.save_button)

        self.layout.addLayout(self.input_layout)

        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.web_view, stretch=1)

        if self.iframe_code:
            self._load_calendar()

    def _save_calendar_iframe(self):
        iframe_code = self.iframe_input.text().strip()
        if iframe_code.startswith("<iframe") and iframe_code.endswith("</iframe>"):
            self.iframe_code = iframe_code
            update_settings({'iframe_code': iframe_code})
            app_logger.info("Saved Google Calendar iframe code.")
            self._load_calendar()
        else:
            QMessageBox.warning(self, "Error", "Invalid iframe code. Please provide a valid iframe.")
            app_logger.warning("Invalid Google Calendar iframe code.")

    def _load_calendar(self):
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    iframe {{ width: 100%; height: 100%; border: none; }}
                </style>
            </head>
            <body>{self.iframe_code}</body>
        </html>
        """
        self.web_view.setHtml(html_content)
        app_logger.info("Loaded Google Calendar iframe.")
