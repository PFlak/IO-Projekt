from openai import OpenAI, OpenAIError
import time
import uuid
from src.utils.logger import app_logger
import multiprocessing
import os
from src.config import DATA_DIRECTORY

class NoteTaker:
    def __init__(self, api_key, format: str):
        self._client = OpenAI(api_key=api_key)
        pass
        
        self.format = format

        if format.upper() not in ['MD', 'HTML', 'LATEX', 'TXT']:
            self.format = 'MD'

        self._format_msg = f' Respond only with {self.format} formatting'
        
    def update_api_key(self, api_key):
        self._client = OpenAI(api_key=api_key)

        app_logger.info(msg=f"NoteTaker: OpenAI api key updated")
        pass

    def update_format(self, format):
        if format.upper() not in ['MD', 'HTML', 'LATEX', 'TXT']:
            self.format = 'MD'
            return
        
        self.format = format

    def create_assistant(self, assistant_name: str='Note taker', assistant_msg: str= None, model:str ='gpt-3.5-turbo'):

        assistants = self._client.beta.assistants.list()

        for ass in assistants:
            if ass.name == ass.name:
                app_logger.info(f"NoteTaker: Assistant {ass.name} exists")
                return ass.id
            
        assistant = self._client.beta.assistants.create(
            model='gpt-3.5-turbo',
            name=assistant_name,
            instructions=assistant_msg
        )

        app_logger.info(f"NoteTaker: Created Assistant {assistant.id}")

        return assistant.id

    def create_thread(self):
        thread = self._client.beta.threads.create(
            messages=[{"role": "user", "content": self._format_msg}] 
        )
        app_logger.info(f'NoteTaker: Created Thread {thread.id}')
        return thread.id

    def generate_notes(self, assistant_id, thread_id, transcription, notes_length='SHORT', callback=None):
        """
        Runs the note generation in a separate process to avoid blocking the UI.
        """
        api_key = self._client.api_key
        process = multiprocessing.Process(
            target=self._generate_notes_worker,
            args=(api_key, assistant_id, thread_id, transcription, notes_length, callback)
        )
        process.start()
        return process

    @staticmethod
    def _generate_notes_worker(api_key, assistant_id, thread_id, transcription, notes_length, callback):
        """Worker function to generate notes in a separate process."""
        if notes_length not in ['SHORT', 'MEDIUM', 'LONG']:
            notes_length = 'SHORT'

        try:
            # Create OpenAI client inside the worker
            client = OpenAI(api_key=api_key)

            # Send message to the thread
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=transcription
            )

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=f'Create {notes_length} summarization of meeting'
            )
            

            # Start the run
            run = client.beta.threads.runs.create(
                assistant_id=assistant_id,
                thread_id=thread_id,
                instructions='Generate only summarization without any other comment'
            )

            # Poll until the run is completed
            while True:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled']:
                    app_logger.error(f"Run failed with status: {run_status.status}")
                    if callback:
                        callback(None)
                    return

                time.sleep(1)  # Avoid excessive polling

            # Retrieve messages from the thread after completion
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            for message in messages.data:  # Latest messages first
                if callback:
                    callback(f'{message.content[0].text.value}')
                    return
                    # Return the AI's response

            if callback:
                callback(None)

        except OpenAIError as e:
            app_logger.error(f"OpenAI API error: {e}")
            if callback:
                callback(None)
        except Exception as e:
            app_logger.error(f"Unexpected error: {e}")
            if callback:
                callback(None)


    def change_note_parameters(self, assistant_id, thread_id, notes_length:str ='SHORT', other_msg:str = None, callback=None):
        api_key = self._client.api_key
        process = multiprocessing.Process(
            target=self.__change_note_parameters_worker,
            args=(api_key, assistant_id, thread_id, notes_length, other_msg, callback)
        )
        process.start()
        return process
    
    @staticmethod
    def __change_note_parameters_worker(api_key, assistant_id, thread_id, transcription, notes_length, other_msg, callback):
        if notes_length not in ['SHORT', 'MEDIUM', 'LONG']:
            notes_length = 'SHORT'

        try:
            # Create OpenAI client inside the worker
            client = OpenAI(api_key=api_key)

            client.beta.threads.messages.create(
                thread_id=thread_id,
                role='user',
                content=f'Create {notes_length} summarization of meeting'
            )

            if other_msg:
                client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role='user',
                    content=other_msg
                )

            # Start the run
            run = client.beta.threads.runs.create(
                assistant_id=assistant_id,
                thread_id=thread_id
            )

            # Poll until the run is completed
            while True:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled']:
                    app_logger.error(f"Run failed with status: {run_status.status}")
                    if callback:
                        callback(None)
                    return

                time.sleep(1)  # Avoid excessive polling

            # Retrieve messages from the thread after completion
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            for message in messages.data:  # Latest messages first
                if callback:
                    callback(f'{message.content[0].text.value}')
                    return
                    # Return the AI's response

            if callback:
                callback(None)

        except OpenAIError as e:
            app_logger.error(f"OpenAI API error: {e}")
            if callback:
                callback(None)
        except Exception as e:
            app_logger.error(f"Unexpected error: {e}")
            if callback:
                callback(None)


def test_callback(result):
    if result:
        print(result)

    else:
        print('Failed to generate notes.')
        
if __name__ == "__main__":

    API_KEY = ''
    TRANSCRIPTION_PATH = ''

    noteTaker = NoteTaker(API_KEY, format='MD')

    ass_id = noteTaker.create_assistant(assistant_msg='You will be a note taker, who make summarization from transcription')

    t_id = noteTaker.create_thread()

    with open(TRANSCRIPTION_PATH, 'r') as transcription:
        transcription_txt = '\n'.join(transcription.readlines())
        proc = noteTaker.generate_notes(assistant_id=ass_id, thread_id=t_id, transcription=transcription_txt, callback=test_callback)
        proc.join()