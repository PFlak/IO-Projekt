from src.services.note_taker import NoteTaker
import json
from src.config import SETTINGS_FILE, DATA_DIRECTORY
import time
from src.utils.logger import app_logger
from src.services.note_taker import NoteTaker
import multiprocessing
import os
import threading
from functools import partial

class NoteManager:
    def __init__(self):
        self.api_key = None
        self.ws_json_list = []
        self.api_key_queue = multiprocessing.Queue()  # Queue to send API key updates
        self.ws_json_queue = multiprocessing.Queue()  # Queue to send workspace JSON updates
        self.generate_notes_queue = multiprocessing.Queue()


        # Process to handle API key updates
        self.__update_api_key_proc = multiprocessing.Process(
            target=self.get_api_key_from_settings_worker,
            args=(self.api_key_queue,)
        )
        self.__update_api_key_proc.start()

        # Process to handle workspace scanning
        self.__scan_data_workspaces_proc = multiprocessing.Process(
            target=self.scan_data_workspaces_worker,
            args=(self.ws_json_queue,)
        )
        self.__scan_data_workspaces_proc.start()

        # Main loop to listen for updates from processes
        self.listener_thread = threading.Thread(target=self.__listen_for_updates, daemon=True)
        self.listener_thread.start()

    def __listen_for_updates(self):
        while True:
            if not self.api_key_queue.empty():
                api_key = self.api_key_queue.get()
                self.cb_get_api_key_from_settings(api_key)
            
            if not self.ws_json_queue.empty():
                ws_json = self.ws_json_queue.get()
                self.cb_scan_data_workspaces(ws_json)

    @staticmethod
    def get_api_key_from_settings_worker(queue):
        while True:
            try:
                with open(SETTINGS_FILE, 'r') as file:
                    settings = json.load(file)
                    queue.put(settings['open_ai_api_key'])  # Send API key back to main process
            except Exception as e:
                app_logger.error(f'NoteManager: Could not update OpenAi Api Key')
            finally:
                time.sleep(2)

    def cb_get_api_key_from_settings(self, api_key: str):
        if api_key == self.api_key:
            return
        self.api_key = api_key
        app_logger.info(f'NoteManager: Api key changed: {self.api_key}')

    @staticmethod
    def scan_data_workspaces_worker(queue):
        while True:
            try:
                dir_list = os.listdir(DATA_DIRECTORY)
                default_json = '''{
                        "ws_name":"", "transcription":false, "transcription_path":"",
                        "can_generate_notes":false, "note_short_path":"", "note_medium_path":"",
                        "note_long_path":"", "thread_id":"", "assistant_name":""
                    }'''

                for ws in dir_list:
                    try:
                        ws_json = json.loads(default_json)
                        ws_json['ws_name'] = ws
                        option_path = os.path.join(DATA_DIRECTORY, ws, 'options.json')

                        if not os.path.exists(option_path):
                            with open(option_path, 'w') as f:
                                json.dump(ws_json, f, indent=4)
                                app_logger.info(f'NoteManager: Options file in {ws} meeting not found. Creating one...')
                            
                            queue.put(ws_json)  # Send the workspace JSON back to main process
                            break
                        
                        with open(option_path, 'r') as f:
                            option_json = json.load(f)

                        ws_json.update(option_json)
                        queue.put(ws_json)  # Send the workspace JSON back to main process
                    except Exception as e:
                        app_logger.error(f"NoteManager: Could not scan {ws}: {e}")

            except Exception as e:
                app_logger.error(f"NoteManager: Could not scan data: {e}")
            finally:
                time.sleep(2)

    def cb_scan_data_workspaces(self, json):
        try:
            for i, ws in enumerate(self.ws_json_list):
                if ws['ws_name'] != json['ws_name']:
                    continue

                if not self.compare_options(ws, json):
                    self.ws_json_list[i] = json
                    app_logger.info(f"NoteManager: Difference detected: {ws['ws_name']}")
                    return
                return

            self.ws_json_list.append(json)
            app_logger.info(f"NoteManager: New ws added: {json['ws_name']}")

        except Exception as e:
            app_logger.error(f"NoteManager: Could not update ws list: {e}")

    def generate_notes(self, ws_name):
        for i, ws in enumerate(self.ws_json_list):
            if ws['ws_name'] != ws_name:
                continue

            if not ws['transcription'] or ws['transcription_path'] == "" or not ws['can_generate_notes']:
                app_logger.error(f"NoteManager: Could not generate notes: No transcription found")
                return
            
            transcription_path = ws['transcription_path']
            transcription_txt = None

            with open(transcription_path, 'r') as f:
                transcription_txt = ''.join(f.readlines())
            
            noteTaker = NoteTaker(self.api_key, 'MD')

            assistant_id = noteTaker.create_assistant()
            thread_id = ws['thread_id']

            if thread_id == '':
                thread_id = noteTaker.create_thread()
                self.ws_json_list[i]['thread_id'] = thread_id

                self.update_options(ws['ws_name'], 'thread_id', thread_id)
            
            callback = partial(self.cb_save_notes, ws_name, 'short')

            proc = noteTaker.generate_notes(assistant_id=assistant_id, thread_id=thread_id, transcription=transcription_txt, callback=callback)
            proc.join()

            callback1 = partial(self.cb_save_notes, ws_name, 'medium')
            proc = noteTaker.modify_notes(assistant_id=assistant_id, thread_id=thread_id, notes_length='MEDIUM', callback=callback1)
            proc.join()

            callback2 = partial(self.cb_save_notes, ws_name, 'long')
            proc = noteTaker.modify_notes(assistant_id=assistant_id, thread_id=thread_id, notes_length='LONG', callback=callback2)
            proc.join()

    @staticmethod
    def cb_save_notes(ws_name, note_type: str, notes):
        """
        Callback function to save generated notes to a specific file.
        
        :param ws: Workspace dictionary containing paths.
        :param notes: The generated notes to save.
        :param note_type: The key for the specific note type to save ('note_short_path', 'note_medium_path', or 'note_long_path').
        """
        try:

            path = os.path.join(DATA_DIRECTORY, ws_name, f"note_{note_type}.txt")

            with open(path, 'w') as file:
                file.write(notes)
            app_logger.info(f"NoteManager: {note_type} saved for workspace {ws_name}")

            NoteManager.update_options(ws_name=ws_name, key=f'note_{note_type.lower()}_path', value=path)
        except Exception as e:
            app_logger.error(f"NoteManager: Failed to save {note_type} for {ws_name}: {e}")

    @staticmethod
    def compare_options(option1, option2):
        for key, value in option2.items():
            if option1[key] != value:
                return False
        return True

    @staticmethod
    def update_options(ws_name, key, value):
        """
        Update a specific key in the options.json file for the given workspace.

        :param ws_name: Name of the workspace
        :param key: The key to update in options.json
        :param value: The new value for the key
        """
        option_path = os.path.join(DATA_DIRECTORY, ws_name, 'options.json')

        if not os.path.exists(option_path):
            app_logger.error(f"NoteManager: options.json not found for workspace '{ws_name}'")
            return

        try:
            with open(option_path, 'r') as file:
                options = json.load(file)

            if key not in options:
                app_logger.warning(f"NoteManager: Key '{key}' not found in options.json for '{ws_name}', adding it.")

            options[key] = value

            with open(option_path, 'w') as file:
                json.dump(options, file, indent=4)

            app_logger.info(f"NoteManager: Updated '{key}' in '{ws_name}/options.json' to '{value}'")

        except Exception as e:
            app_logger.error(f"NoteManager: Failed to update options.json for '{ws_name}': {e}")

if __name__ == '__main__':
    nodeManager = NoteManager()
    time.sleep(2)
    nodeManager.generate_notes('sample_meeting')
