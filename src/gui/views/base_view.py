from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class BaseView(QWidget):
    def __init__(self, title):
        super().__init__()

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Label
        label = QLabel(title, font=QFont("Consolas", 20))
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label.setMargin(10)
        self.layout.addWidget(label)

        # Font
        self.setFont(QFont("Consolas", 10))
