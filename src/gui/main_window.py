from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QStackedWidget
from src.gui.navigation_panel import NavigationPanel
from src.gui.views.calendar_view import CalendarView
from src.gui.views.main_view import MainView
from src.gui.views.notes_view import NotesView
from src.gui.views.settings_view import SettingsView
from src.utils.logger import app_logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        app_logger.info("Initializing MainWindow")
        self.setWindowTitle("SmartNotesApp")
        self.resize(800, 600)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QHBoxLayout(self.central_widget)

        # Navigation panel and content area
        self.navigation_panel = NavigationPanel(self)
        self.content_area = QStackedWidget(self)

        # Add views to the content area
        self.main_view = MainView()
        self.notes_view = NotesView()
        self.calendar_view = CalendarView()
        self.settings_view = SettingsView()

        self.content_area.addWidget(self.main_view)
        self.content_area.addWidget(self.notes_view)
        self.content_area.addWidget(self.calendar_view)
        self.content_area.addWidget(self.settings_view)

        # Connect navigation
        self.navigation_panel.main_button.clicked.connect(lambda: self.switch_view(self.main_view))
        self.navigation_panel.notes_button.clicked.connect(lambda: self.switch_view(self.notes_view))
        self.navigation_panel.calendar_button.clicked.connect(lambda: self.switch_view(self.calendar_view))
        self.navigation_panel.settings_button.clicked.connect(lambda: self.switch_view(self.settings_view))

        # Add navigation panel and content area to the layout
        self.layout.addWidget(self.navigation_panel)
        self.layout.addWidget(self.content_area)

        # Show default view
        self.switch_view(self.main_view)

    def switch_view(self, view):
        self.content_area.setCurrentWidget(view)
        app_logger.info(f"Switched to view: {view.__class__.__name__}")
