from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QSizePolicy

from src.config import settings, update_settings
from src.gui.views.base_view import BaseView
from src.utils.logger import app_logger


class CalendarView(BaseView):
    def __init__(self):
        super().__init__("Google Calendar")
        self.calendar_url = settings.get('calendar_url', '')
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignCenter)

        self.instruction_label = QLabel("Make sure your Google Calendar is set to public for proper display.")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.input_layout.addWidget(self.instruction_label)

        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste here link to your Google Calendar")
        self.url_input.setFixedWidth(500)
        form_layout.addWidget(self.url_input, alignment=Qt.AlignCenter)

        self.save_button = QPushButton("Save")
        self.save_button.setFixedWidth(200)
        self.save_button.clicked.connect(self._save_calendar_url)
        form_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.input_layout.addLayout(form_layout)
        main_layout.addLayout(self.input_layout)

        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addLayout(main_layout)

        if self.calendar_url:
            self._load_calendar()

    def _save_calendar_url(self):
        url = self.url_input.text().strip()
        if url.startswith("https://") and "calendar.google.com" in url:
            self.calendar_url = url
            update_settings({'calendar_url': url})
            app_logger.info("Saved Google Calendar URL.")
            self._load_calendar()
        else:
            QMessageBox.warning(self, "Error", "Invalid URL. Please provide a valid Google Calendar link.")
            app_logger.warning("Invalid Google Calendar URL.")

    def _load_calendar(self):
        self.instruction_label.hide()
        self.url_input.hide()
        self.save_button.hide()

        if not self.web_view.parent():
            self.layout.addWidget(self.web_view, stretch=1)

        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    iframe {{ width: 100%; height: 100%; border: none; }}
                </style>
            </head>
            <body>
                <iframe src="{self.calendar_url}" style="border: 0" frameborder="0" scrolling="no"></iframe>
            </body>
        </html>
        """
        self.web_view.setHtml(html_content)
        app_logger.info("Loaded Google Calendar URL.")
