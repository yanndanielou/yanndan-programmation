import threading
import time
import tkinter as tk
from tkinter import Toplevel, messagebox, simpledialog, StringVar
from typing import Callable, List, cast

import pygame
import pyttsx3, pyttsx3.voice
from PIL import Image, ImageTk


import random

from logger import logger_config

DEFAULT_PLAYER_NAME = "Carabistouille"

DEVINETTES_QUESTION_REPONSE = [("Comment s'appelle ton chat?", "Moka"), ("Quel est le prénom de ton papa?", "Yann"), ("Quel est le prénom de ta maman?", "Céline")]

EXPECTED_LANGUAGE_IN_VOICE_NAME = "french"


class GameMainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.pyttsx3_engine = pyttsx3.init()

        current_voice: str = self.pyttsx3_engine.getProperty("voice")
        if "fr-fr" not in current_voice:
            logger_config.print_and_log_info(f"Default voice {current_voice} is not french. Change voice")

            for voice in (cast(pyttsx3.voice.Voice, n) for n in self.pyttsx3_engine.getProperty("voices")):
                logger_config.print_and_log_info(f"voice: {voice}, voice.id: {voice.id}, voice.languages: {voice.languages}, voice.name: {voice.name}, voice.gender: {voice.gender}")
                if EXPECTED_LANGUAGE_IN_VOICE_NAME.lower() in cast(str, voice.name).lower():
                    logger_config.print_and_log_info(
                        f"voice found for {EXPECTED_LANGUAGE_IN_VOICE_NAME}: {voice}, voice.id: {voice.id}, voice.languages: {voice.languages}, voice.name: {voice.name}, voice.gender: {voice.gender}"
                    )
                    # self.pyttsx3_engine.setProperty("voice", voice.name)
                    self.pyttsx3_engine.setProperty("voice", voice.id)

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
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            AdditionExercise(self, switch_mode_callback=self.switch_mode, first_number=random.randint(0, 20), second_number=random.randint(0, 10)),
            RecognizeSyllabeInChoiceWithVoiceExercise(self, self.switch_mode),
            ListenNumberAndTypeExercise(self, self.switch_mode),
            ListenNumberAndTypeExercise(self, self.switch_mode),
            ListenNumberAndTypeExercise(self, self.switch_mode),
            ListenNumberAndTypeExercise(self, self.switch_mode),
            ListenNumberAndTypeExercise(self, self.switch_mode),
            ListenNumberAndTypeExercise(self, self.switch_mode),
        ]

        self.current_mode_index = 0
        self.show_current_mode()

    def prompt_for_name(self) -> None:
        self.synthetise_and_play_sentence(f"Comment t'appelles-tu?")
        child_name_entered = simpledialog.askstring("Bienvenue", "Entrez votre prénom :")
        self.child_name = child_name_entered if child_name_entered else DEFAULT_PLAYER_NAME
        self.synthetise_and_play_sentence(f"Tu t'appelles {self.child_name}")
        # self.show_current_mode()

    def guess_to_enter_game(self) -> None:

        devinette, expected_answer = DEVINETTES_QUESTION_REPONSE[random.randint(0, len(DEVINETTES_QUESTION_REPONSE))]
        expected_answer = expected_answer.lower()
        answer_given = ""
        while answer_given.lower() != expected_answer:
            self.synthetise_and_play_sentence(devinette)
            answer_given = simpledialog.askstring("Devinette", devinette).lower()

            if answer_given == expected_answer:
                self.synthetise_and_play_sentence(f"Bonne réponse champion! {self.child_name}")

            self.synthetise_and_play_sentence(f"Mauvaise réponse, recommence. La bonne réponse est {expected_answer}")

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

        self.synthetise_and_play_sentence(sentence=congrats_text, blocking=True)

        message_label.pack(pady=10)

        popup.after(15000, popup.destroy)
        popup.bind("<Return>", lambda _: popup.destroy())
        popup.focus()

        popup.wait_window(popup)

    def exercise_won(self) -> None:
        self.points += 1
        self.update_header()
        self.congrats_player()

    def synthetise_and_play_sentence(self, sentence: str, blocking: bool = True) -> None:
        self.pyttsx3_engine.say(sentence)
        if blocking:
            self.pyttsx3_engine.runAndWait()
        else:
            threading.Thread(target=self.pyttsx3_engine.runAndWait).start()


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

    def check_answer(self) -> None:
        pass


class TextAnswerInEntryExercise(ModexFrame):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None], expected_result: str, give_answer_on_error: bool) -> None:
        super().__init__(game_main_window, switch_mode_callback)
        self.answer_entry = tk.Entry(self)
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", lambda _: self.check_answer())

        self.expected_result = expected_result
        logger_config.print_and_log_info(f"expected_result {self.expected_result}")

    def start_exercise(self) -> None:
        super().start_exercise()
        logger_config.print_and_log_info(f"expected_result {self.expected_result}")
        self.answer_entry.focus()

    def check_answer(self) -> None:
        answer_given = self.answer_entry.get()
        logger_config.print_and_log_info(f"answer:{answer_given}")

        self.game_main_window.synthetise_and_play_sentence(f"Tu as écris {answer_given}")

        if answer_given == self.expected_result:
            self.exercise_won()
        else:
            self.exercise_retry(True)

    def exercise_retry(self, give_answer: bool) -> None:
        if give_answer:
            self.game_main_window.synthetise_and_play_sentence(f"Mauvaise réponse. Il fallait écrire {self.expected_result}. Recommence!")
        else:
            self.game_main_window.synthetise_and_play_sentence("Mauvaise réponse. Recommence!")


class AdditionExercise(TextAnswerInEntryExercise):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None], first_number: int = random.randint(0, 20), second_number: int = random.randint(0, 10)) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback, expected_result=f"{first_number + second_number}", give_answer_on_error=True)

        self.consigne_label_value.set(f"{first_number} + {second_number}")
        logger_config.print_and_log_info(f"Consigne:{self.consigne_label_value.get()}")

        self.first_number = first_number
        self.second_number = second_number

    def say_consigne(self) -> None:
        super().say_consigne()
        self.game_main_window.synthetise_and_play_sentence(f"Calcule la somme de {self.first_number} et {self.second_number}")


class ListenNumberAndTypeExercise(ModexFrame):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None]) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback)

        self.number_to_guess = f"{random.randint(0, 40)}"
        logger_config.print_and_log_info(f"number_to_guess {self.number_to_guess}")

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
        self.game_main_window.synthetise_and_play_sentence(f"Ecrire le chiffre {self.number_to_guess}")
        # self.game_main_window.synthetise_and_play_sentence(f"{self.number_to_guess}")

    def check_answer(self) -> None:
        answer_given = self.answer_entry.get()
        logger_config.print_and_log_info(f"answer:{answer_given}")

        if answer_given == self.number_to_guess:
            self.exercise_won()
        else:
            self.exercise_retry()

    def exercise_retry(self) -> None:
        answer_given = self.answer_entry.get()

        self.game_main_window.synthetise_and_play_sentence(f"Mauvaise réponse. Tu as écrit {answer_given}, il fallait écrire {self.number_to_guess}. Recommence!")
        self.game_main_window.synthetise_and_play_sentence(f"Ecrire le chiffre {self.number_to_guess}")


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
        self.game_main_window.synthetise_and_play_sentence(self.expected_answer)

    def check_answer(self, answer_given: str) -> None:

        if answer_given == self.expected_answer:
            self.exercise_won()
        else:
            self.game_main_window.synthetise_and_play_sentence(f"Mauvaise réponse. Tu as choisit {answer_given}, il fallait écrire {self.expected_answer}. Recommence!")


if __name__ == "__main__":
    with logger_config.application_logger("nombres_et_syllabes"):
        jeu = GameMainWindow()
        jeu.mainloop()
