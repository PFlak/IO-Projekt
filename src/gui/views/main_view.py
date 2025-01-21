from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy

from src.gui.components.postprocessing_panel import PostProcessingPanel
from src.gui.components.recording_panel import RecordingPanel
from src.gui.views.base_view import BaseView


class MainView(BaseView):
    """
    The main view of the application, providing the primary user interface.

    The MainView includes two panels:
    - A recording panel for capturing audio or video.
    - A post-processing panel for handling recorded data.

    Inherits from `BaseView`.

    Attributes
    ----------
    recording_panel : RecordingPanel
        A panel for recording audio or video.
    post_processing_panel : PostProcessingPanel
        A panel for post-processing recorded data.

    Methods
    -------
    _setup_ui()
        Configures the user interface layout for the main view.
    """

    def __init__(self):
        """
        Initializes the MainView instance.

        Sets the title of the view to "Main View" and configures the user interface by calling `_setup_ui`.
        """
        super().__init__("Main View")
        self._setup_ui()

    def _setup_ui(self):
        """
        Configures the user interface components and layout for the main view.

        The layout includes:
        - A left panel for recording functionality (`RecordingPanel`).
        - A right panel for post-processing (`PostProcessingPanel`).
        - A vertical line separator between the two panels.
        """
        main_layout = QVBoxLayout()
        split_layout = QHBoxLayout()

        # Left Panel - Recording
        self.recording_panel = RecordingPanel()

        # Right Panel - Post-processing
        self.post_processing_panel = PostProcessingPanel()

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        separator.setFixedWidth(2)

        split_layout.addWidget(self.recording_panel)
        split_layout.addWidget(separator)
        split_layout.addWidget(self.post_processing_panel)

        main_layout.addLayout(split_layout)

        self.layout.addLayout(main_layout)
