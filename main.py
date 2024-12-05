import sys
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.utils.logger import app_logger


def main():
    app_logger.info("Starting application")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = app.exec()
    app_logger.info("Application exited with code: %s", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
