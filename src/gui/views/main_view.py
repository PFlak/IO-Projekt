from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Widok Główny")
        layout.addWidget(label)
