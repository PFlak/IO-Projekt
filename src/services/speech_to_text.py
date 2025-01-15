import whisper
import os
from src.utils.logger import app_logger
from src.config import settings


class SpeechToText:
    def __init__(self):
        model_size = settings.get('model_size', 'small')
        transcription_language = settings.get('transcription_language', 'pl')

        try:
            app_logger.info(f"Loading Whisper model: {model_size}")
            self.model = whisper.load_model(model_size)
            self.transcription_language = transcription_language
            app_logger.info(f"Whisper model loaded successfully with language: {transcription_language}")
        except Exception as e:
            app_logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Error loading Whisper model: {e}")

    def transcribe_audio(self, audio_path):
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
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(transcription)
            app_logger.info(f"Transcription saved to {output_path}")
        except Exception as e:
            app_logger.error(f"Failed to save transcription: {e}")
            raise RuntimeError(f"Error saving transcription: {e}")
