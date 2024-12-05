from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Widok Ustawień")
        layout.addWidget(label)
