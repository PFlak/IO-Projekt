from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt


class PostProcessingPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.post_processing_label = QLabel("Post-processing placeholder")
        layout.addWidget(self.post_processing_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)
