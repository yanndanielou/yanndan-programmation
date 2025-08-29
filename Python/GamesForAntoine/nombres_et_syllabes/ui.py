import random
import tkinter as tk
from tkinter import Toplevel, simpledialog
from typing import List

import pygame

from common import string_utils, text_to_speach
from logger import logger_config
from PIL import Image, ImageTk

import labyrinthe
from nombres_et_syllabes.exercises_bank import (
    HeaderFrame,
    ModexFrame,
)

DEFAULT_PLAYER_NAME = "Carabistouille"

DEVINETTES_QUESTION_REPONSE = [("Comment s'appelle ton chat?", "Moka"), ("Quel est le prénom de ton papa?", "Yann"), ("Quel est le prénom de ta maman?", "Céline")]

EXPECTED_LANGUAGE_IN_VOICE_NAME = "french"

FRENCH_SYLLABES_SUFFIXES = [""]


class GameMainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.text_to_speech_manager = text_to_speach.TextToSpeechManager()
        self.text_to_speech_manager.change_voice_to_language(language_long_name=text_to_speach.FRENCH_LANGUAGE_LONG_NAME, language_short_name=text_to_speach.FRENCH_LANGUAGE_SHORT_NAME)

        self.title("Jeu éducatif")
        self.geometry("400x300")

        pygame.mixer.init()

        self.felicitation_image = ImageTk.PhotoImage(Image.open("felicitation.png"))

        self.child_name = ""
        self.points = 0

        self.prompt_for_name()
        self.guess_to_enter_game()

        self.modes: List[ModexFrame] = []
        self.header_frame = HeaderFrame(self)
        self.header_frame.pack(fill=tk.X)
        self.current_mode_index = 0

    def prompt_for_name(self) -> None:
        self.synthetise_and_play_sentence("Comment t'appelles-tu?", blocking=False)
        child_name_entered = simpledialog.askstring("Bienvenue", "Entrez votre prénom :")
        self.child_name = child_name_entered if child_name_entered else DEFAULT_PLAYER_NAME
        self.synthetise_and_play_sentence(f"Tu t'appelles {self.child_name}", blocking=False)

    def guess_to_enter_game(self) -> None:

        devinette, expected_answer = DEVINETTES_QUESTION_REPONSE[random.randint(0, len(DEVINETTES_QUESTION_REPONSE) - 1)]
        expected_answer_used = string_utils.without_diacritics(expected_answer.lower())
        logger_config.print_and_log_info(f"expected_answer_used:{expected_answer_used}")

        answer_given_used = ""
        while answer_given_used != expected_answer_used:
            self.synthetise_and_play_sentence(devinette, blocking=False)
            answer_given = simpledialog.askstring("Devinette", devinette)
            logger_config.print_and_log_info(f"answer_given:{answer_given}")
            answer_given_used = string_utils.without_diacritics(answer_given.lower())
            logger_config.print_and_log_info(f"answer_given_used:{answer_given_used}")

            if answer_given_used == expected_answer_used:
                self.synthetise_and_play_sentence(f"Bonne réponse champion! {self.child_name}", blocking=False)

            else:
                self.synthetise_and_play_sentence(f"Mauvaise réponse (tu as entré {answer_given}). Recommence. La bonne réponse est {expected_answer}", blocking=False)

    def update_header(self) -> None:
        self.header_frame.update_info(self.child_name, self.points)

    def show_current_mode(self) -> None:
        self.update_header()

        for mode in self.modes:
            mode.pack_forget()

        self.modes[self.current_mode_index].start_exercise()

    def switch_mode(self) -> None:
        self.current_mode_index = (self.current_mode_index + 1) % len(self.modes)
        self.show_current_mode()

    def congrats_player(self) -> None:
        popup = Toplevel(self)
        popup.title("Bravo champion!")

        felicitation_label = tk.Label(popup, image=self.felicitation_image)
        felicitation_label.pack(pady=10)

        congrats_text = f"Bonne réponse {self.child_name} ! Tu as {self.points} points champion!!"
        message_label = tk.Label(popup, text=congrats_text, font=("Arial", 12))

        self.synthetise_and_play_sentence(sentence=congrats_text, blocking=False)

        message_label.pack(pady=10)

        popup.after(2000, popup.destroy)
        popup.bind("<Return>", lambda _: popup.destroy())
        popup.focus()

        popup.wait_window(popup)

    def exercise_won(self) -> None:
        self.points += 1
        self.update_header()
        self.congrats_player()
        # labyrinthe.MazeGame(root=self, size=self.points + 3, embedded_in_other_application=True)

    def synthetise_and_play_sentence(self, sentence: str, blocking: bool) -> None:
        self.text_to_speech_manager.synthetise_and_play_sentence(sentence=sentence, blocking=blocking)
