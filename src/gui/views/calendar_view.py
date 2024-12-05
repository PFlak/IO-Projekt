from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class CalendarView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Widok Kalendarza")
        layout.addWidget(label)
