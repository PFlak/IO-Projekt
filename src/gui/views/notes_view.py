from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class NotesView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Widok Przeglądu Notatek")
        layout.addWidget(label)
