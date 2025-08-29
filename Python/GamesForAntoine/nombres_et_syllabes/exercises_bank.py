import random
import tkinter as tk
from enum import Enum, auto
from tkinter import NO, StringVar
from typing import TYPE_CHECKING, Callable

from logger import logger_config

from abc import abstractmethod, ABC

if TYPE_CHECKING:
    from nombres_et_syllabes.ui import GameMainWindow

DEFAULT_PLAYER_NAME = "Carabistouille"

DEVINETTES_QUESTION_REPONSE = [("Comment s'appelle ton chat?", "Moka"), ("Quel est le prénom de ton papa?", "Yann"), ("Quel est le prénom de ta maman?", "Céline")]

EXPECTED_LANGUAGE_IN_VOICE_NAME = "french"

FRENCH_SYLLABES_SUFFIXES = [""]


class HeaderFrame(tk.Frame):
    def __init__(self, master: "GameMainWindow") -> None:
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
    @abstractmethod
    def __init__(self, game_main_window: "GameMainWindow") -> None:
        super().__init__(game_main_window)
        self.game_main_window = game_main_window
        self.switch_mode_callback = game_main_window.switch_mode

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
    @abstractmethod
    def __init__(self, game_main_window: "GameMainWindow", expected_result: str, give_answer_on_error: bool) -> None:
        super().__init__(game_main_window)

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
            self.exercise_lost_retry(self.give_answer_on_error)

    def exercise_lost_retry(self, give_answer: bool) -> None:
        self.answer_entry.delete(0)
        if give_answer:
            self.game_main_window.synthetise_and_play_sentence(f"Mauvaise réponse. Il fallait écrire {self.expected_result}. Recommence!", blocking=False)
        else:
            self.game_main_window.synthetise_and_play_sentence("Mauvaise réponse. Recommence!", blocking=False)


class AdditionExercise(TextAnswerInEntryExercise):
    def __init__(self, game_main_window: "GameMainWindow", first_number: int = random.randint(0, 20), second_number: int = random.randint(0, 10)) -> None:
        super().__init__(game_main_window=game_main_window, expected_result=f"{first_number + second_number}", give_answer_on_error=True)

        self.consigne_label_value.set(f"{first_number} + {second_number}")
        logger_config.print_and_log_info(f"Consigne:{self.consigne_label_value.get()}")

        self.first_number = first_number
        self.second_number = second_number

    def say_consigne(self) -> None:
        super().say_consigne()
        self.game_main_window.synthetise_and_play_sentence(f"Calcule la somme de {self.first_number} plus {self.second_number}", blocking=False)


class SoustractionExercise(TextAnswerInEntryExercise):
    def __init__(self, game_main_window: "GameMainWindow", first_number: int = random.randint(0, 20), second_number: int = random.randint(0, 10)) -> None:
        super().__init__(game_main_window=game_main_window, expected_result=f"{first_number - second_number}", give_answer_on_error=True)

        self.consigne_label_value.set(f"{first_number} - {second_number}")
        logger_config.print_and_log_info(f"Consigne:{self.consigne_label_value.get()}")

        self.first_number = first_number
        self.second_number = second_number

    def say_consigne(self) -> None:
        super().say_consigne()
        self.game_main_window.synthetise_and_play_sentence(f"Calcule la différence de {self.first_number} moins {self.second_number}", blocking=False)


class DoubleExercise(AdditionExercise):
    def __init__(self, game_main_window: "GameMainWindow", number: int = random.randint(0, 20)) -> None:
        super().__init__(game_main_window=game_main_window, first_number=number, second_number=number)


class ListenAndTypeExercise(ModexFrame, ABC):

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

    @abstractmethod
    def __init__(self, game_main_window: "GameMainWindow", item_to_listen_and_learn: ItemToListenAndType) -> None:
        super().__init__(game_main_window=game_main_window)

        self.consigne_label_value.set(f"Ecoute et écris {item_to_listen_and_learn.type_label()}")

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
            self.exercise_lost_retry()

    def exercise_lost_retry(self) -> None:
        answer_given = self.answer_entry.get()

        self.answer_entry.delete(0)
        self.game_main_window.synthetise_and_play_sentence(
            sentence=f"Mauvaise réponse. Tu as écrit {answer_given}, il fallait écrire {self.item_to_listen_and_learn.answer_label()}. Recommence!", blocking=False
        )
        self.game_main_window.synthetise_and_play_sentence(sentence=f"Ecrire le {self.item_to_listen_and_learn.type_label()}  {self.item_to_listen_and_learn.answer_label()}", blocking=False)


class ListenAndTypeNumberExercise(ListenAndTypeExercise):
    def __init__(self, game_main_window: "GameMainWindow", number: int) -> None:
        super().__init__(game_main_window, ListenAndTypeExercise.NumberToListenAndType(number=number))


class ListenAndTypeWordExercise(ListenAndTypeExercise):
    def __init__(self, game_main_window: "GameMainWindow", word: str) -> None:
        super().__init__(game_main_window, ListenAndTypeExercise.WordToListenAndType(word=word))


class RecognizeSyllabeInChoiceWithVoiceExercise(ModexFrame):
    def __init__(self, game_main_window: "GameMainWindow") -> None:
        super().__init__(game_main_window=game_main_window)

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
