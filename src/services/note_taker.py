from openai import OpenAI, OpenAIError
import time
import uuid
from src.utils.logger import app_logger
import multiprocessing
import os
from src.config import DATA_DIRECTORY

class NoteTaker:
    """
    A class for managing note-taking using OpenAI's API.
    
    Attributes:
        _client (OpenAI): The OpenAI client for API interactions.
        format (str): The format for generated notes (MD, HTML, LaTeX, or TXT).
        _format_msg (str): Instruction for the assistant on formatting.
    """
    
    def __init__(self, api_key, format: str):
        """
        Initializes the NoteTaker with an API key and desired note format.
        
        Args:
            api_key (str): The OpenAI API key.
            format (str): Desired format for the notes ('MD', 'HTML', 'LATEX', 'TXT').
        """
        self._client = OpenAI(api_key=api_key)
        self.format = format.upper() if format.upper() in ['MD', 'HTML', 'LATEX', 'TXT'] else 'MD'
        self._format_msg = f' Respond only with {self.format} formatting'
        
    def update_api_key(self, api_key):
        """
        Updates the OpenAI API key.
        
        Args:
            api_key (str): The new API key.
        """
        self._client = OpenAI(api_key=api_key)
        app_logger.info(msg=f"NoteTaker: OpenAI API key updated")
        
    def update_format(self, format):
        """
        Updates the format of the generated notes.
        
        Args:
            format (str): The new format ('MD', 'HTML', 'LATEX', 'TXT').
        """
        self.format = format.upper() if format.upper() in ['MD', 'HTML', 'LATEX', 'TXT'] else 'MD'
        
    def create_assistant(self, assistant_name: str = 'Note taker', assistant_msg: str = None, model: str = 'gpt-3.5-turbo'):
        """
        Creates an assistant for note-taking if it does not already exist.
        
        Args:
            assistant_name (str): The name of the assistant.
            assistant_msg (str): Instructions for the assistant.
            model (str): OpenAI model to use.
        
        Returns:
            str: The assistant ID.
        """
        assistants = self._client.beta.assistants.list()
        for ass in assistants:
            if ass.name == assistant_name:
                app_logger.info(f"NoteTaker: Assistant {ass.name} exists")
                return ass.id
        
        assistant = self._client.beta.assistants.create(
            model=model,
            name=assistant_name,
            instructions=assistant_msg
        )
        app_logger.info(f"NoteTaker: Created Assistant {assistant.id}")
        return assistant.id
    
    def create_thread(self):
        """
        Creates a thread for managing note-taking sessions.
        
        Returns:
            str: The thread ID.
        """
        thread = self._client.beta.threads.create(
            messages=[{"role": "user", "content": self._format_msg}]
        )
        app_logger.info(f'NoteTaker: Created Thread {thread.id}')
        return thread.id
    
    def generate_notes(self, assistant_id, thread_id, transcription, notes_length='SHORT', callback=None):
        """
        Generates notes asynchronously in a separate process.
        
        Args:
            assistant_id (str): The ID of the assistant.
            thread_id (str): The ID of the thread.
            transcription (str): The transcription text to summarize.
            notes_length (str): The desired length of notes ('SHORT', 'MEDIUM', 'LONG').
            callback (function, optional): Function to process results.
        
        Returns:
            multiprocessing.Process: The process handling note generation.
        """
        api_key = self._client.api_key
        process = multiprocessing.Process(
            target=self._generate_notes_worker,
            args=(api_key, assistant_id, thread_id, transcription, notes_length, callback)
        )
        process.start()
        return process
    
    def modify_notes(self, assistant_id, thread_id, notes_length='SHORT', callback=None):
        api_key = self._client.api_key
        process = multiprocessing.Process(
            target=self._modify_notes_worker,
            args=(api_key, assistant_id, thread_id, notes_length, callback)
        )
        process.start()
        return process

    @staticmethod
    def _generate_notes_worker(api_key, assistant_id, thread_id, transcription, notes_length, callback):
        """
        Worker function to generate notes in a separate process.
        """
        if notes_length not in ['SHORT', 'MEDIUM', 'LONG']:
            notes_length = 'SHORT'
        
        try:
            client = OpenAI(api_key=api_key)
            client.beta.threads.messages.create(thread_id=thread_id, role='user', content=transcription)
            client.beta.threads.messages.create(thread_id=thread_id, role='user', content=f'Create {notes_length} summarization of meeting')
            run = client.beta.threads.runs.create(assistant_id=assistant_id, thread_id=thread_id)
            
            while True:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled']:
                    app_logger.error(f"Run failed with status: {run_status.status}")
                    if callback:
                        callback(None)
                    return
                time.sleep(1)
            
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            for message in messages.data:
                if callback:
                    callback(f'{message.content[0].text.value}')
                    return
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

    @staticmethod
    def _modify_notes_worker(api_key, assistant_id, thread_id, notes_length, callback):
        if notes_length not in ['SHORT', 'MEDIUM', 'LONG']:
            notes_length = 'SHORT'
        
        try:
            client = OpenAI(api_key=api_key)
            client.beta.threads.messages.create(thread_id=thread_id, role='user', content=f'Create {notes_length} summarization of meeting')
            run = client.beta.threads.runs.create(assistant_id=assistant_id, thread_id=thread_id)
            
            while True:
                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled']:
                    app_logger.error(f"Run failed with status: {run_status.status}")
                    if callback:
                        callback(None)
                    return
                time.sleep(1)
            
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            for message in messages.data:
                if callback:
                    callback(f'{message.content[0].text.value}')
                    return
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
