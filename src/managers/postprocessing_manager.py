from PySide6.QtCore import QObject, Signal

class PostProcessingManager(QObject):
    """
    Manages the status of post-processing tasks.

    Attributes:
        status_changed (Signal): A signal emitted when a status changes.
    """

    status_changed = Signal(str, str)  # Signal to notify (process_name, new_status)

    _status = {
        "recording": "not_started",
        "transcription": "not_started",
        "notes": "not_started",
    }

    @classmethod
    def get_status(cls, process_name):
        """Returns the current status of a given process."""
        return cls._status.get(process_name, "not_started")

    @classmethod
    def update_status(cls, process_name, status):
        """
        Updates the status of a process and emits a signal.

        Parameters:
        process_name (str): The name of the process to update.
        status (str): The new status ("not_started", "started", "finished", "error").
        """
        if process_name in cls._status:
            cls._status[process_name] = status
            cls.status_changed.emit(process_name, status)
