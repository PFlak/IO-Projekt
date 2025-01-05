import os
import wave

import pyaudiowpatch as pyaudio

from src.utils.logger import app_logger


class AudioRecorder:
    def __init__(self, session_dir):
        self.wave_file = None
        self.session_dir = session_dir
        self.audio_chunk = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.audio_stream = None
        self.audio_interface = None
        self.is_recording = False

    def _get_default_speakers(self):
        try:
            audio_interface = pyaudio.PyAudio()
            wasapi_info = audio_interface.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = audio_interface.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

            if not default_speakers["isLoopbackDevice"]:
                for loopback in audio_interface.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        return loopback
                raise RuntimeError("Default loopback output device not found.")

            return default_speakers
        except Exception as e:
            raise RuntimeError(f"Audio device initialization failed: {e}")

    def start_recording(self):
        try:
            app_logger.info("Starting audio recording.")
            self.audio_interface = pyaudio.PyAudio()
            default_speakers = self._get_default_speakers()

            self.channels = default_speakers["maxInputChannels"]
            self.rate = int(default_speakers["defaultSampleRate"])

            wave_file_path = os.path.join(self.session_dir, "audio.wav")
            self.wave_file = wave.open(wave_file_path, 'wb')
            self.wave_file.setnchannels(self.channels)
            self.wave_file.setsampwidth(pyaudio.get_sample_size(self.audio_format))
            self.wave_file.setframerate(self.rate)

            def callback(in_data, frame_count, time_info, status):
                self.wave_file.writeframes(in_data)
                return in_data, pyaudio.paContinue

            self.audio_stream = self.audio_interface.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.audio_chunk,
                input_device_index=default_speakers["index"],
                stream_callback=callback
            )

            self.is_recording = True
            self.audio_stream.start_stream()
        except Exception as e:
            app_logger.error(f"Audio recording error: {e}")
            self.stop_recording()

    def stop_recording(self):
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.audio_interface:
            self.audio_interface.terminate()
        if hasattr(self, 'wave_file') and self.wave_file:
            self.wave_file.close()
        self.is_recording = False
        app_logger.info("Audio recording stopped.")
