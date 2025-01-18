from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy

from src.gui.components.postprocessing_panel import PostProcessingPanel
from src.gui.components.recording_panel import RecordingPanel
from src.gui.views.base_view import BaseView


class MainView(BaseView):
    def __init__(self):
        super().__init__("Main View")
        self._setup_ui()

    def _setup_ui(self):
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
