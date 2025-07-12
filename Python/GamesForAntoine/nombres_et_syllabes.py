import threading
import time
import tkinter as tk
from tkinter import Toplevel, messagebox, simpledialog, StringVar
from typing import Callable, List, cast

import pygame
import pyttsx3, pyttsx3.voice
from PIL import Image, ImageTk

from common import text_to_speach

from enum import Enum, auto

import random

from logger import logger_config

DEFAULT_PLAYER_NAME = "Carabistouille"

DEVINETTES_QUESTION_REPONSE = [("Comment s'appelle ton chat?", "Moka"), ("Quel est le prénom de ton papa?", "Yann"), ("Quel est le prénom de ta maman?", "Céline")]

EXPECTED_LANGUAGE_IN_VOICE_NAME = "french"


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

        self.header_frame = HeaderFrame(self)
        self.header_frame.pack(fill=tk.X)

        self.modes: List[ModexFrame] = [
            ListenAndTypeExercise(self, self.switch_mode, ListenAndTypeExercise.NumberToListenAndType(number=random.randint(0, 10))),
            ListenAndTypeExercise(self, self.switch_mode, ListenAndTypeExercise.NumberToListenAndType(number=random.randint(0, 20))),
            ListenAndTypeExercise(self, self.switch_mode, ListenAndTypeExercise.NumberToListenAndType(number=random.randint(0, 30))),
            DoubleExercise(self, switch_mode_callback=self.switch_mode, number=random.randint(0, 5)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 9), second_number=random.randint(0, 5)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 10), second_number=random.randint(0, 8)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            RecognizeSyllabeInChoiceWithVoiceExercise(self, self.switch_mode),
        ]

        self.current_mode_index = 0
        self.show_current_mode()

    def prompt_for_name(self) -> None:
        self.synthetise_and_play_sentence("Comment t'appelles-tu?", blocking=False)
        child_name_entered = simpledialog.askstring("Bienvenue", "Entrez votre prénom :")
        self.child_name = child_name_entered if child_name_entered else DEFAULT_PLAYER_NAME
        self.synthetise_and_play_sentence(f"Tu t'appelles {self.child_name}", blocking=False)

    def guess_to_enter_game(self) -> None:

        devinette, expected_answer = DEVINETTES_QUESTION_REPONSE[random.randint(0, len(DEVINETTES_QUESTION_REPONSE) - 1)]
        expected_answer = expected_answer.lower()
        answer_given = ""
        while answer_given.lower() != expected_answer:
            self.synthetise_and_play_sentence(devinette, blocking=False)
            answer_given = simpledialog.askstring("Devinette", devinette)

            if answer_given == expected_answer:
                self.synthetise_and_play_sentence(f"Bonne réponse champion! {self.child_name}", blocking=False)

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

    def synthetise_and_play_sentence(self, sentence: str, blocking: bool) -> None:
        self.text_to_speech_manager.synthetise_and_play_sentence(sentence=sentence, blocking=blocking)


class HeaderFrame(tk.Frame):
    def __init__(self, master: GameMainWindow) -> None:
        super().__init__(master, bg="lightblue")
        self.name_label = tk.Label(self, text="", bg="lightblue", font=("Arial", 14, "bold"))
        self.name_label.pack(side=tk.LEFT, padx=10)
        self.points_label = tk.Label(self, text="", bg="lightblue", font=("Arial", 14, "bold"))
        self.points_label.pack(side=tk.RIGHT, padx=10)
        self.update_info(master.child_name, master.points)

    def update_info(self, name: str, points: int) -> None:
        self.name_label.config(text=f"Prénom: {name}")
        self.points_label.config(text=f"Points: {points}")


class ModexFrame(tk.Frame):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None]) -> None:
        super().__init__(game_main_window)
        self.game_main_window = game_main_window
        self.switch_mode_callback = switch_mode_callback

        self.consigne_label_value = StringVar()
        self.consigne_label_value.set("Consigne")
        self.consigne_label = tk.Label(self, textvariable=self.consigne_label_value)
        self.consigne_label.pack(pady=10)

    def exercise_won(self) -> None:
        self.game_main_window.exercise_won()
        self.switch_mode_callback()

    def start_exercise(self) -> None:
        self.say_consigne()
        self.pack()
        self.focus()

    def say_consigne(self) -> None:
        # self.game_main_window.synthetise_and_play_sentence(sentence="Consigne de l'exercice")
        pass


class TextAnswerInEntryExercise(ModexFrame):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None], expected_result: str, give_answer_on_error: bool) -> None:
        super().__init__(game_main_window, switch_mode_callback)
        self.answer_entry = tk.Entry(self)
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", lambda _: self.check_answer())
        self.give_answer_on_error = give_answer_on_error

        self.expected_result = expected_result
        logger_config.print_and_log_info(f"expected_result {self.expected_result}")

    def start_exercise(self) -> None:
        super().start_exercise()
        logger_config.print_and_log_info(f"expected_result {self.expected_result}")
        self.answer_entry.focus()

    def check_answer(self) -> None:
        answer_given = self.answer_entry.get()
        logger_config.print_and_log_info(f"answer:{answer_given}")

        self.game_main_window.synthetise_and_play_sentence(f"Tu as écris {answer_given}", blocking=False)

        if answer_given == self.expected_result:
            self.exercise_won()
        else:
            self.exercise_retry(self.give_answer_on_error)

    def exercise_retry(self, give_answer: bool) -> None:
        if give_answer:
            self.game_main_window.synthetise_and_play_sentence(f"Mauvaise réponse. Il fallait écrire {self.expected_result}. Recommence!", blocking=False)
        else:
            self.game_main_window.synthetise_and_play_sentence("Mauvaise réponse. Recommence!", blocking=False)


class AdditionExercise(TextAnswerInEntryExercise):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None], first_number: int = random.randint(0, 20), second_number: int = random.randint(0, 10)) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback, expected_result=f"{first_number + second_number}", give_answer_on_error=True)

        self.consigne_label_value.set(f"{first_number} + {second_number}")
        logger_config.print_and_log_info(f"Consigne:{self.consigne_label_value.get()}")

        self.first_number = first_number
        self.second_number = second_number

    def say_consigne(self) -> None:
        super().say_consigne()
        self.game_main_window.synthetise_and_play_sentence(f"Calcule la somme de {self.first_number} plus {self.second_number}", blocking=False)


class DoubleExercise(AdditionExercise):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None], number: int = random.randint(0, 20)) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback, first_number=number, second_number=number)


class ListenAndTypeExercise(ModexFrame):

    class ExerciseType(Enum):
        WORD = auto()
        NUMBER = auto()

    class ItemToListenAndType:
        def __init__(self) -> None:
            pass

        def type_label(self) -> str:
            return ""

        def answer_label(self) -> str:
            return ""

    class NumberToListenAndType(ItemToListenAndType):
        def __init__(self, number: int) -> None:
            self.exercise_type = ListenAndTypeExercise.ExerciseType.NUMBER
            self.number = number

        def type_label(self) -> str:
            return "le nombre"

        def answer_label(self) -> str:
            return f"{self.number}"

    class WordToListenAndType(ItemToListenAndType):
        def __init__(self, word: str) -> None:
            self.exercise_type = ListenAndTypeExercise.ExerciseType.WORD
            self.word = word

        def type_label(self) -> str:
            return "le mot"

        def answer_label(self) -> str:
            return f"{self.word}"

    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None], item_to_listen_and_learn: ItemToListenAndType) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback)

        self.item_to_listen_and_learn = item_to_listen_and_learn
        logger_config.print_and_log_info(f"{item_to_listen_and_learn.type_label()} to_guess {self.item_to_listen_and_learn.answer_label()}")

        self.answer_entry = tk.Entry(self)
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", lambda _: self.check_answer())

        check_button = tk.Button(self, text="Vérifier", command=self.check_answer)
        check_button.pack(pady=5)

    def start_exercise(self) -> None:
        super().start_exercise()
        self.answer_entry.focus()

    def say_consigne(self) -> None:
        super().say_consigne()
        self.game_main_window.synthetise_and_play_sentence(sentence=f"Ecrire {self.item_to_listen_and_learn.type_label()}  {self.item_to_listen_and_learn.answer_label()}", blocking=False)

    def check_answer(self) -> None:
        answer_given = self.answer_entry.get()
        logger_config.print_and_log_info(f"answer:{answer_given}")

        if answer_given.lower() == self.item_to_listen_and_learn.answer_label().lower():
            self.exercise_won()
        else:
            self.exercise_retry()

    def exercise_retry(self) -> None:
        answer_given = self.answer_entry.get()

        self.game_main_window.synthetise_and_play_sentence(
            sentence=f"Mauvaise réponse. Tu as écrit {answer_given}, il fallait écrire {self.item_to_listen_and_learn.answer_label()}. Recommence!", blocking=False
        )
        self.game_main_window.synthetise_and_play_sentence(sentence=f"Ecrire le {self.item_to_listen_and_learn.type_label()}  {self.item_to_listen_and_learn.answer_label()}", blocking=False)


class RecognizeSyllabeInChoiceWithVoiceExercise(ModexFrame):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None]) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback)

        self.syllabes = ["pa", "ma", "la"]
        self.expected_answer = "ma"

        label = tk.Label(self, text="Écouter et cliquer sur la syllabe")
        label.pack(pady=10)

        play_sound_button = tk.Button(self, text="Jouer le son", command=self.say_syllabe)
        play_sound_button.pack(pady=5)

        for syllabe in self.syllabes:
            button = tk.Button(self, text=syllabe, command=lambda s=syllabe: self.check_answer(s))
            button.pack(padx=2)

    def say_consigne(self) -> None:
        super().say_consigne()
        self.game_main_window.synthetise_and_play_sentence("Clique sur la syllabe", blocking=True)
        self.say_syllabe()

    def say_syllabe(self) -> None:
        self.game_main_window.synthetise_and_play_sentence(sentence=self.expected_answer, blocking=False)

    def check_answer(self, answer_given: str) -> None:

        if answer_given == self.expected_answer:
            self.exercise_won()
        else:
            self.game_main_window.synthetise_and_play_sentence(sentence=f"Mauvaise réponse. Tu as choisit {answer_given}, il fallait écrire {self.expected_answer}. Recommence!", blocking=False)


if __name__ == "__main__":
    with logger_config.application_logger("nombres_et_syllabes"):
        jeu = GameMainWindow()
        jeu.mainloop()
