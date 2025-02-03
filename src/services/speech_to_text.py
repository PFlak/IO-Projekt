import torch
import whisper
import os
from src.utils.logger import app_logger
from src.config import settings


class SpeechToText:
    """
    A class for transcribing audio files to text using the Whisper model.

    The class initializes a Whisper model for transcription and provides methods for
    transcribing audio and saving the transcription.

    Attributes
    ----------
    model : whisper.Model
        The Whisper model instance used for transcription.
    transcription_language : str
        The language used for transcriptions, as specified in settings.

    Methods
    -------
    transcribe_audio(audio_path)
        Transcribes the given audio file to text.
    save_transcription(transcription, output_path)
        Saves the transcribed text to a file.
    """

    def __init__(self):
        """
        Initializes the SpeechToText class by loading the Whisper model.

        The model size and transcription language are fetched from the application settings.

        :raises RuntimeError: If the Whisper model fails to load.
        """
        model_size = settings.get('model_size', 'small')
        transcription_language = settings.get('transcription_language', 'pl')

        device = "cuda" if torch.cuda.is_available() else "cpu"

        try:
            app_logger.info(f"Loading Whisper model: {model_size} on device: {device}")
            self.model = whisper.load_model(model_size, device=device)
            self.transcription_language = transcription_language
            app_logger.info(f"Whisper model loaded successfully with language: {transcription_language}")
        except Exception as e:
            app_logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Error loading Whisper model: {e}")

    def transcribe_audio(self, audio_path):
        """
        Transcribes the given audio file to text.

        :param audio_path: The path to the audio file to transcribe.
        :type audio_path: str
        :returns: The transcription of the audio file.
        :rtype: str

        :raises FileNotFoundError: If the specified audio file does not exist.
        :raises ValueError: If the audio file format is not supported.
        :raises RuntimeError: If an error occurs during transcription.
        """
        if not os.path.isfile(audio_path):
            app_logger.error(f"Audio file not found: {audio_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not audio_path.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
            app_logger.error(f"Unsupported audio format: {audio_path}")
            raise ValueError("Unsupported audio format. Supported formats: WAV, MP3, M4A, FLAC.")

        try:
            app_logger.info(f"Starting transcription for: {audio_path} in language: {self.transcription_language}")
            result = self.model.transcribe(audio_path, language=self.transcription_language)
            transcription = result.get("text", "")
            app_logger.info("Transcription completed successfully.")
            return transcription
        except Exception as e:
            app_logger.error(f"Error during transcription: {e}")
            raise RuntimeError(f"Error during transcription: {e}")

    def save_transcription(self, transcription, output_path):
        """
        Saves the transcription to a specified file.

        :param transcription: The transcription text to save.
        :type transcription: str
        :param output_path: The path to the file where the transcription will be saved.
        :type output_path: str

        :raises RuntimeError: If an error occurs while saving the transcription.
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(transcription)
            app_logger.info(f"Transcription saved to {output_path}")
        except Exception as e:
            app_logger.error(f"Failed to save transcription: {e}")
            raise RuntimeError(f"Error saving transcription: {e}")
