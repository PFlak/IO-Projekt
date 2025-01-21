import os
import json

# Application metadata
APP_NAME = "SmartNotesApp"
APP_VERSION = "1.0.0"

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_DIRECTORY = os.path.join(BASE_DIR, 'logs')
ICON_DIRECTORY = os.path.join(BASE_DIR, 'assets', 'icons')
SRC_DIR = os.path.join(BASE_DIR, 'src')
SETTINGS_FILE = os.path.join(SRC_DIR, 'settings.json')

# Default settings
DEFAULT_SETTINGS = {
    "data_directory": os.path.join(BASE_DIR, 'data'),
    "calendar_url": "",
    "model_size": "small",
    "transcription_language": "pl",
    "max_data_size_gb": 5,
    "open_ai_api_key": ""
}

# Ensure settings file exists with default settings
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)

# Load settings
with open(SETTINGS_FILE, 'r') as f:
    settings = json.load(f)

# Paths from settings
DATA_DIRECTORY = settings.get('data_directory', DEFAULT_SETTINGS['data_directory'])

# Ensure necessary directories exist
os.makedirs(LOG_DIRECTORY, exist_ok=True)
os.makedirs(DATA_DIRECTORY, exist_ok=True)


def update_settings(new_settings):
    settings.update(new_settings)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)
