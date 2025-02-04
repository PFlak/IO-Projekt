from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from src.managers.postprocessing_manager import postProcessingManager

class PostProcessingPanel(QWidget):
    """
    A panel for handling post-processing tasks in the application.
    This panel allows users to manage recording, transcription, and note creation.

    Attributes:
        process_label (QLabel): A label displaying the text "Process".
        recording_label (QLabel): A label displaying the text for recording.
        transcription_label (QLabel): A label displaying the text for creating transcription.
        notes_label (QLabel): A label displaying the text for creating notes.
        recording_box (QWidget): A box representing the status of the recording task.
        transcription_box (QWidget): A box representing the status of the transcription task.
        notes_box (QWidget): A box representing the status of the notes creation task.

    Methods:
        _setup_ui(): Initializes the UI components and layout for the post-processing panel.
        update_box_status(box, status): Updates the color and text color of the given box based on the status.
    """

    def __init__(self):
        """
        Initializes the PostProcessingPanel instance and sets up the UI.

        This constructor calls the parent constructor and then sets up the user interface.
        """
        super().__init__()
        self._setup_ui()

        postProcessingManager.status_changed.connect(self.on_status_changed)

    def _setup_ui(self):
        """
        Sets up the UI components for the post-processing panel.

        This method creates the layout for the panel, adds labels and boxes for each post-processing task,
        and configures the layout alignment and spacing.
        """
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Process label
        self.process_label = QLabel("Process")
        layout.addWidget(self.process_label, alignment=Qt.AlignCenter)

        # Recording box and label
        self.recording_box = self.create_status_box("Recording")
        layout.addWidget(self.recording_box, alignment=Qt.AlignCenter)

        # Transcription box and label
        self.transcription_box = self.create_status_box("Creating Transcription")
        layout.addWidget(self.transcription_box, alignment=Qt.AlignCenter)

        # Notes box and label
        self.notes_box = self.create_status_box("Creating Notes")
        layout.addWidget(self.notes_box, alignment=Qt.AlignCenter)


        self.setLayout(layout)

    def create_status_box(self, text):
        """
        Creates a status box with the given text and default gray color.

        Parameters:
        text (str): The text to display inside the box.

        Returns:
        QWidget: The created status box widget.
        """
        box = QWidget()
        box.setFixedSize(300, 50)
        box.setStyleSheet("background-color: gray; color: white;")

        box_layout = QHBoxLayout()
        box_layout.setAlignment(Qt.AlignCenter)
        box_label = QLabel(text)
        box_layout.addWidget(box_label)

        box.setLayout(box_layout)
        return box

    def update_box_status(self, box, status):
        """
        Updates the color and text color of the given box based on the status.

        Parameters:
        box (QWidget): The box to update the color of.
        status (str): The status of the task ("not_started", "started", "finished", "error").
        """
        color_map = {
            "not_started": ("gray", "white"),
            "started": ("yellow", "black"),
            "finished": ("green", "black"),
            "error": ("red", "black")
        }
        background_color, text_color = color_map.get(status, ("gray", "white"))
        box.setStyleSheet(f"background-color: {background_color}; color: {text_color};")

    def on_status_changed(self, process_name, new_status):
        """
        Handles status change signals from PostProcessingManager.

        Parameters:
        process_name (str): Name of the process that changed.
        new_status (str): The new status.
        """
        if process_name == "recording":
            self.update_box_status(self.recording_box, new_status)
        elif process_name == "transcription":
            self.update_box_status(self.transcription_box, new_status)
        elif process_name == "notes":
            self.update_box_status(self.notes_box, new_status)

# Example usage:
# panel = PostProcessingPanel()
# panel.update_box_status(panel.recording_box, "started")
# panel.update_box_status(panel.transcription_box, "finished")
# panel.update_box_status(panel.notes_box, "error")
