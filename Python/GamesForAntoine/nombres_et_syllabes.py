import threading
import time
import tkinter as tk
from tkinter import Toplevel, messagebox, simpledialog
from typing import Callable

import pygame
import pyttsx3
from PIL import Image, ImageTk

import random

from logger import logger_config

DEFAULT_PLAYER_NAME = "Carabistouille"


class GameMainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.pyttsx3_engine = pyttsx3.init()

        self.title("Jeu éducatif")
        self.geometry("400x300")  # Définir une taille pour l'application

        # Initialiser pygame pour le son
        pygame.mixer.init()

        # Charger l'image de félicitations
        self.felicitation_image = ImageTk.PhotoImage(Image.open("felicitation.png"))

        # Variables pour nom et score
        self.child_name = ""
        self.points = 0

        # Obtenir le prénom de l'enfant
        self.prompt_for_name()

        # Créer des frames
        self.header_frame = HeaderFrame(self)
        self.header_frame.pack(fill=tk.X)

        self.mode1_frame = ListenNumberAndType(self, self.show_mode2)
        self.mode2_frame = RecognizeSyllabeInChoiceWithVoice(self, self.show_mode1)

        # Afficher le premier mode
        self.show_mode1()

    def prompt_for_name(self) -> None:
        """Demande le prénom de l'enfant au démarrage."""
        child_name_entered = simpledialog.askstring("Bienvenue", "Entrez votre prénom :")
        self.child_name = child_name_entered if child_name_entered else DEFAULT_PLAYER_NAME
        self.synthetise_and_play_sentence(f"Tu t'appelles {self.child_name}")

    def update_header(self) -> None:
        """Met à jour le header avec le nouveau score et nom."""
        self.header_frame.update_info(self.child_name, self.points)

    def show_mode1(self) -> None:
        self.update_header()
        self.mode2_frame.pack_forget()
        self.mode1_frame.pack()

    def show_mode2(self) -> None:
        self.update_header()
        self.mode1_frame.pack_forget()
        self.mode2_frame.pack()

    def congrats_player(self) -> None:
        """Afficher une fenêtre popup personnalisée de félicitations."""
        popup = Toplevel(self)
        popup.title("Bravo!")
        # popup.geometry("300x300")

        felicitation_label = tk.Label(popup, image=self.felicitation_image)
        felicitation_label.pack(pady=10)

        congrats_text = f"Bonne réponse ! Vous avez gagné un point. Vous avez {self.points} points"
        message_label = tk.Label(popup, text=congrats_text, font=("Arial", 12))

        self.synthetise_and_play_sentence(sentence=congrats_text, blocking=False)

        message_label.pack(pady=10)

        # Fermer le popup automatiquement après 15 secondes ou à l'appui sur "Entrée"
        popup.after(15000, popup.destroy)
        popup.bind("<Return>", lambda _: popup.destroy())

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
        self.master = game_main_window

    def exercise_won(self) -> None:
        self.game_main_window.exercise_won()
        self.switch_mode_callback()


class ListenNumberAndType(ModexFrame):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None]) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback)

        self.number_to_guess = f"{random.randint(3, 12)}"
        logger_config.print_and_log_info(f"number_to_guess {self.number_to_guess}")
        self.say_consigne()

        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", lambda _: self.check_answer())  # Associer la touche "Entrée" à la validation

        check_button = tk.Button(self, text="Vérifier", command=self.check_answer)
        check_button.pack(pady=5)

    def say_consigne(self) -> None:
        self.game_main_window.synthetise_and_play_sentence(sentence="Consigne de l'exercice")
        time.sleep(0.5)
        self.game_main_window.synthetise_and_play_sentence("Écouter et écrire le chiffre", blocking=True)
        time.sleep(1)
        self.game_main_window.synthetise_and_play_sentence(f"{self.number_to_guess}", blocking=True)

    def check_answer(self) -> None:
        answer = self.entry.get()
        logger_config.print_and_log_info(f"answer:{answer}")

        if answer == self.number_to_guess:
            self.exercise_won()
        else:
            self.exercise_retry()

    def exercise_retry(self) -> None:
        self.game_main_window.synthetise_and_play_sentence("Mauvaise réponse, essaie encore!")
        self.say_consigne()


class RecognizeSyllabeInChoiceWithVoice(ModexFrame):
    def __init__(self, game_main_window: GameMainWindow, switch_mode_callback: Callable[[], None]) -> None:
        super().__init__(game_main_window=game_main_window, switch_mode_callback=switch_mode_callback)

        self.syllabes = ["pa", "ma", "la"]

        label = tk.Label(self, text="Mode 2: Écouter et cliquer sur la syllabe")
        label.pack(pady=10)

        play_sound_button = tk.Button(self, text="Jouer le son", command=self.play_sound)
        play_sound_button.pack(pady=5)

        for syllabe in self.syllabes:
            button = tk.Button(self, text=syllabe, command=lambda s=syllabe: self.check_answer(s))
            button.pack(side=tk.LEFT, padx=2)

        prev_button = tk.Button(self, text="Précédent", command=self.switch_mode_callback)
        prev_button.pack(pady=10)

    def play_sound(self) -> None:
        pygame.mixer.music.load("syllabe.mp3")  # Placez le chemin de votre fichier mp3 ici
        pygame.mixer.music.play()

    def check_answer(self, syllabe: str) -> None:
        correct_syllabe = "pa"  # Remplacez cela par la logique correcte
        if syllabe == correct_syllabe:
            self.exercise_won()


if __name__ == "__main__":
    with logger_config.application_logger("nombres_et_syllabes"):
        jeu = GameMainWindow()
        jeu.mainloop()
