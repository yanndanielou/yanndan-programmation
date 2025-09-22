# -*-coding:Utf-8 -*

import threading
from threading import Thread

from queue import Queue
import logging
from typing import List, cast, Optional

import pyttsx3, pyttsx3.voice

from logger import logger_config

FRENCH_LANGUAGE_LONG_NAME = "french"
FRENCH_LANGUAGE_SHORT_NAME = "FR-FR"


class TextToSpeechManager:
    def __init__(self) -> None:
        self.pyttsx3_engine = pyttsx3.init()
        self.queue: Queue = Queue()
        self.running: bool = False
        self.thread: Optional[threading.Thread] = None

    def _play_from_queue(self) -> None:
        while self.running:
            sentence = self.queue.get()
            if sentence is None:
                break
            self.pyttsx3_engine.say(sentence)
            self.pyttsx3_engine.runAndWait()

    def synthetise_and_play_sentence(self, sentence: str, blocking: bool = True) -> None:
        logger_config.print_and_log_info(f"synthetise_and_play_sentence: {sentence}, blocking:{blocking}")

        if blocking:
            # Wait for any existing non-blocking process to complete
            if self.thread and self.thread.is_alive():
                self.queue.put(None)  # Signal the thread to complete
                self.thread.join()  # Wait for the thread to finish

            # Blocking call
            self.pyttsx3_engine.say(sentence)
            self.pyttsx3_engine.runAndWait()
        else:
            # Non-blocking call using thread and queue
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._play_from_queue, daemon=True)
                self.thread.start()
            self.queue.put(sentence)

    def stop(self) -> None:
        # Stop the playback and clear the queue
        logger_config.print_and_log_info("TextToSpeechManager: Stop")

        self.queue.put(None)
        self.running = False
        if self.thread:
            self.thread.join()
        self.pyttsx3_engine.stop()

    def change_voice_to_language(self, language_long_name: str, language_short_name: str) -> bool:
        current_voice: str = self.pyttsx3_engine.getProperty("voice")
        if language_short_name not in current_voice:
            logger_config.print_and_log_info(f"Default voice {current_voice} is not {language_long_name}. Change voice")

            for voice in (cast(pyttsx3.voice.Voice, n) for n in self.pyttsx3_engine.getProperty("voices")):
                logging.info(f"voice: {voice}, voice.id: {voice.id}, voice.languages: {voice.languages}, voice.name: {voice.name}, voice.gender: {voice.gender}")
                voice_name = cast(str, voice.name).lower()
                language_long_name = language_long_name.lower()
                if language_long_name in voice_name:
                    logger_config.print_and_log_info(
                        f"voice found for {language_long_name}: voice.id: {voice.id}, voice.languages: {voice.languages}, voice.name: {voice.name}, voice.gender: {voice.gender}"
                    )
                    # self.pyttsx3_engine.setProperty("voice", voice.name)
                    self.pyttsx3_engine.setProperty("voice", voice.id)
                    return True
                else:
                    logging.info(f"{language_long_name} not found in {voice_name}")

            logger_config.print_and_log_error(
                f"could not find voice {language_long_name} {language_short_name} among \n{[f"{voice.name} {voice.id} {voice.languages} {voice.gender} \\n" for voice in  self.pyttsx3_engine.getProperty("voices")]}"
            )

        return False


# Example Usage
if __name__ == "__main__":
    tts = TextToSpeechManager()
    tts.synthetise_and_play_sentence("Hello World", blocking=False)
    tts.synthetise_and_play_sentence("This is a test sentence", blocking=False)
    # To stop the non-blocking queue processing
    tts.stop()
