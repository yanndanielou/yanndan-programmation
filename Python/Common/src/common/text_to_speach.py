# -*-coding:Utf-8 -*

import threading
import logging
from typing import List, cast

import pyttsx3, pyttsx3.voice

from logger import logger_config

FRENCH_LANGUAGE_LONG_NAME = "french"
FRENCH_LANGUAGE_SHORT_NAME = "FR-FR"


class TextToSpeachManager:
    """allows simple int counter"""

    def __init__(self) -> None:
        self.pyttsx3_engine = pyttsx3.init()

    def change_voice_to_language(self, language_long_name: str, language_short_name: str) -> bool:
        current_voice: str = self.pyttsx3_engine.getProperty("voice")
        if language_short_name not in current_voice:
            logger_config.print_and_log_info(f"Default voice {current_voice} is not {language_long_name}. Change voice")

            for voice in (cast(pyttsx3.voice.Voice, n) for n in self.pyttsx3_engine.getProperty("voices")):
                logging.info(f"voice: {voice}, voice.id: {voice.id}, voice.languages: {voice.languages}, voice.name: {voice.name}, voice.gender: {voice.gender}")
                if language_long_name.lower() in cast(str, voice.name).lower():
                    logger_config.print_and_log_info(
                        f"voice found for {language_long_name}: {voice}, voice.id: {voice.id}, voice.languages: {voice.languages}, voice.name: {voice.name}, voice.gender: {voice.gender}"
                    )
                    # self.pyttsx3_engine.setProperty("voice", voice.name)
                    self.pyttsx3_engine.setProperty("voice", voice.id)
                    return True

        logger_config.print_and_log_error(f"could not find voicee {language_long_name} {language_short_name} among {self.pyttsx3_engine.getProperty("voices")}")

        return False

    def synthetise_and_play_sentence(self, sentence: str, blocking: bool = True) -> None:
        self.pyttsx3_engine.say(sentence)
        if blocking:
            self.pyttsx3_engine.runAndWait()
        else:
            threading.Thread(target=self.pyttsx3_engine.runAndWait).start()
