from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QStackedWidget, QFrame, QMessageBox
from PySide6.QtGui import QGuiApplication, QIcon
from src.gui.navigation_panel import NavigationPanel
from src.gui.views.calendar_view import CalendarView
from src.gui.views.main_view import MainView
from src.gui.views.notes_view import NotesView
from src.gui.views.settings_view import SettingsView
from src.utils.logger import app_logger
from src.config import ICON_DIRECTORY, APP_NAME
import os


class MainWindow(QMainWindow):
    """
    Main application window for the user interface.

    The MainWindow class is the central interface for the application. It includes a navigation panel,
    content area with multiple views, and manages switching between those views. The window is configured
    with a title, icon, and size based on the screen's available geometry.

    Inherits from `QMainWindow`.

    Attributes
    ----------
    central_widget : QWidget
        The main central widget of the window.
    layout : QHBoxLayout
        The layout managing the navigation panel, separator line, and content area.
    navigation_panel : NavigationPanel
        The navigation panel on the left side of the window.
    content_area : QStackedWidget
        The content area displaying the main, notes, calendar, and settings views.
    main_view : MainView
        The main view displayed by the content area.
    notes_view : NotesView
        The notes view displayed by the content area.
    calendar_view : CalendarView
        The calendar view displayed by the content area.
    settings_view : SettingsView
        The settings view displayed by the content area.
    separator_line : QFrame
        A vertical line separating the navigation panel from the content area.

    Methods
    -------
    switch_view(view)
        Switches the current view in the content area.
    closeEvent(event)
        Handles the close event, ensuring any active recording is stopped before exiting.
    """

    def __init__(self):
        """
        Initializes the MainWindow instance.

        The initialization sets the window's title, icon, size, and position. It also creates and configures
        the navigation panel, content area, and layout.

        The navigation panel buttons are connected to their respective views in the content area.
        """
        super().__init__()
        app_logger.info("Initializing MainWindow")

        # Set title, icon, size and position
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(os.path.join(ICON_DIRECTORY, 'app.ico')))
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen.width() // 4, screen.height() // 4, screen.width() // 2, screen.height() // 2)

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

        # Separator line between navigation panel and content area
        self.separator_line = QFrame()
        self.separator_line.setFrameShape(QFrame.VLine)
        self.separator_line.setFrameShadow(QFrame.Sunken)

        # Add navigation panel, separator line, and content area to the layout
        self.layout.addWidget(self.navigation_panel)
        self.layout.addWidget(self.separator_line)
        self.layout.addWidget(self.content_area)

        # Show default view
        self.switch_view(self.main_view)

    def switch_view(self, view):
        """
        Switches the current view in the content area.

        :param view: The view to display in the content area.
        :type view: QWidget
        """
        self.content_area.setCurrentWidget(view)
        app_logger.info(f"Switched to view: {view.__class__.__name__}")

    def closeEvent(self, event):
        """
        Handles the close event for the window.

        If a recording is in progress, prompts the user to confirm whether to stop recording and exit the application.

        :param event: The close event.
        :type event: QCloseEvent
        """
        if self.main_view.recording_panel.is_recording:
            reply = QMessageBox.question(self, 'Recording in Progress',
                                         'Recording is in progress. Do you want to stop and exit?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.main_view.recording_panel.stop_recording()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
