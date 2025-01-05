import os

# Application metadata
APP_NAME = "SmartNotesApp"
APP_VERSION = "1.0.0"

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_DIRECTORY = os.path.join(BASE_DIR, 'logs')
ICON_DIRECTORY = os.path.join(BASE_DIR, 'assets', 'icons')
DATA_DIRECTORY = os.path.join(BASE_DIR, 'data')

# Ensure necessary directories exist
os.makedirs(LOG_DIRECTORY, exist_ok=True)
os.makedirs(DATA_DIRECTORY, exist_ok=True)
