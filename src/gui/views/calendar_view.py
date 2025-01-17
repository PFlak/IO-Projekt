from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QLabel, QSizePolicy

from src.config import settings
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

        if self.calendar_url:
            self._load_calendar(main_layout)
        else:
            instruction_label = QLabel("Set up your Google Calendar URL in the settings.")
            instruction_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(instruction_label)

        self.layout.addLayout(main_layout)

    def _load_calendar(self, layout):
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.web_view, stretch=1)

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
