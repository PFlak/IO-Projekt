from PySide6.QtWidgets import QPushButton, QLineEdit, QTextEdit, QLabel, QCheckBox, QFileDialog, QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from src.gui.views.base_view import BaseView
import os

class MainView(BaseView):
    def __init__(self):
        super().__init__("Widok główny")
        main_layout = self.layout
        
        # Create a top section for left-right split
        top_layout = QHBoxLayout()
        
        # Left layout for upload button
        left_layout = QVBoxLayout()
        self.file_button = self.create_button("Wybierz plik spotkania")
        self.file_button.clicked.connect(self.select_meeting_file)
        self.file_label = QLabel("Nie wybrano pliku")

        # Left layout
        left_layout.addStretch()
        left_layout.addWidget(self.file_button, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.file_label, alignment=Qt.AlignCenter)
        left_layout.addStretch()
        
        # Right layout for the input fields and checkboxes
        right_layout = QVBoxLayout()
        
        # Meeting details
        self.meeting_title = QLineEdit(self)
        self.meeting_title.setPlaceholderText("Tytuł...")
        self.meeting_title.setStyleSheet("QLineEdit { padding: 10px; }")
        self.meeting_title.setMinimumSize(200, 10)
        self.meeting_title_checkbox = QCheckBox("Automatycznie")

        self.participants = self.create_button("Uczestnicy...")
        self.participants.clicked.connect(self.select_csv_file)
        self.participants_label = QLabel("Nie wybrano pliku CSV")

        self.agenda = QTextEdit(self)
        self.agenda.setPlaceholderText("Plan...")
        self.agenda.setStyleSheet("QLineEdit { padding: 10px; }")
        self.agenda.setMinimumSize(200, 10)
        self.agenda.setMaximumSize(200, 100)
        self.agenda_checkbox = QCheckBox("Automatycznie")
        
        self.meeting_title_checkbox.toggled.connect(self.toggle_auto)
        self.agenda_checkbox.toggled.connect(self.toggle_auto)

        # Right layout
        right_layout.addStretch()
        right_layout.addWidget(QLabel("Wprowadź szczegóły"), alignment=Qt.AlignHCenter)
        right_layout.addStretch()

        right_layout.addWidget(self.meeting_title, alignment=Qt.AlignHCenter)
        right_layout.addWidget(self.meeting_title_checkbox, alignment=Qt.AlignHCenter)

        right_layout.addStretch()
        right_layout.addWidget(self.create_line(QFrame.HLine))
        
        right_layout.addWidget(self.participants, alignment=Qt.AlignHCenter)
        right_layout.addWidget(self.participants_label, alignment=Qt.AlignHCenter)

        right_layout.addStretch()
        right_layout.addWidget(self.create_line(QFrame.HLine))

        right_layout.addWidget(self.agenda, alignment=Qt.AlignHCenter)
        right_layout.addWidget(self.agenda_checkbox, alignment=Qt.AlignHCenter)
        right_layout.addStretch()
        
        # Bottom layout for the "Start" button centered at the bottom
        bottom_layout = QVBoxLayout()
        self.generate_pdf_button = self.create_button("Rozpocznij")
        self.generate_pdf_button.clicked.connect(self.generate)
        bottom_layout.addWidget(self.generate_pdf_button, alignment=Qt.AlignHCenter)
        
        # Add layouts
        top_layout.addLayout(left_layout)
        top_layout.addWidget(self.create_line(QFrame.VLine))
        top_layout.addLayout(right_layout)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        # Set main layout for the view
        self.setLayout(main_layout)

    def toggle_auto(self):
        self.meeting_title.setDisabled(self.meeting_title_checkbox.isChecked())
        self.agenda.setDisabled(self.agenda_checkbox.isChecked())

        if self.meeting_title_checkbox.isChecked(): self.meeting_title.clear()
        if self.agenda_checkbox.isChecked(): self.agenda.clear()

    def select_meeting_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Wybierz plik spotkania", "", "Pliki audio/wideo (*.mp3 *.wav *.mp4)")
        if file:
            self.file_label.setText(os.path.basename(file))
    
    def select_csv_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Wybierz plik z listą uczestników", "", "Plik wartości rozdzielanych przecinkami (*.csv)")
        if file:
            self.participants_label.setText(os.path.basename(file))

    def create_button(self, text):
        button = QPushButton(text, self)
        button.setStyleSheet("QPushButton { padding: 10px 20px; }")
        return button

    def create_line(self, type):
        line = QFrame(self)
        line.setFrameShape(type)
        line.setFrameShadow(QFrame.Sunken)
        return line
    
    def generate(self):
        # PLACEHOLDER
        return None
