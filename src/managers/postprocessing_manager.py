from PySide6.QtCore import QObject, Signal

class PostProcessingManager(QObject):
    """
    Manages the status of post-processing tasks.

    Attributes:
        status_changed (Signal): A signal emitted when a status changes.
    """
    status_changed = Signal(str, str)

    def __init__(self,):
        super().__init__()


        self._status = {
            "recording": "not_started",
            "transcription": "not_started",
            "notes": "not_started",
        }

    def get_status(self, process_name):
        """Returns the current status of a given process."""
        return self._status.get(process_name, "not_started")

    def update_status(self, process_name, status):
        """
        Updates the status of a process and emits a signal.

        Parameters:
        process_name (str): The name of the process to update.
        status (str): The new status ("not_started", "started", "finished", "error").
        """
        if process_name in self._status:
            self._status[process_name] = status
            self.status_changed.emit(process_name, status)

postProcessingManager = PostProcessingManager()
