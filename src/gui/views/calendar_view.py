from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QLabel, QSizePolicy

from src.config import settings
from src.gui.views.base_view import BaseView
from src.utils.logger import app_logger


class CalendarView(BaseView):
    """
    A view displaying a Google Calendar embedded in the application.

    This view loads a Google Calendar URL provided in the application settings and displays it
    using a web view. If no URL is configured, it prompts the user to set up the Google Calendar URL.

    Inherits from `BaseView`.

    Attributes
    ----------
    calendar_url : str
        The URL of the Google Calendar to be displayed. Default is an empty string if not set in settings.

    Methods
    -------
    _setup_ui()
        Configures the user interface for displaying the Google Calendar or a setup instruction message.
    _load_calendar(layout)
        Loads and embeds the Google Calendar URL into a web view.
    """

    def __init__(self):
        """
        Initializes the CalendarView instance.

        Retrieves the calendar URL from the application settings and calls `_setup_ui` to configure the UI.
        """
        super().__init__("Google Calendar")
        self.calendar_url = settings.get('calendar_url', '')
        self._setup_ui()

    def _setup_ui(self):
        """
        Configures the user interface for the CalendarView.

        If a valid calendar URL is configured in the settings, it loads and displays the calendar.
        If no URL is configured, a message instructing the user to set it up in the settings is shown.
        """
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
        """
        Loads and displays the Google Calendar URL in a web view.

        Creates an embedded HTML view containing the Google Calendar and sets it to a `QWebEngineView`.

        Parameters
        ----------
        layout : QVBoxLayout
            The layout to which the web view is added.
        """
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
                <iframe src="{self.calendar_url}" style="border: 0;{'filter: invert(1) hue-rotate(180deg);' if self.palette().color(self.backgroundRole()).lightness() < 128 else ''}" frameborder="0" scrolling="no"></iframe>
            </body>
        </html>
        """
        self.web_view.setHtml(html_content)
        app_logger.info("Loaded Google Calendar URL.")
