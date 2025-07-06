import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import pygame
from typing import Callable


class Jeu(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Jeu éducatif")

        # Initialiser pygame pour le son
        pygame.mixer.init()

        # Charger l'image de félicitations
        self.felicitation_image = ImageTk.PhotoImage(Image.open("Felicitations.png"))

        # Créer des frames
        self.mode1_frame = Mode1Frame(self, self.show_mode2)
        self.mode2_frame = Mode2Frame(self, self.show_mode1)

        # Label pour afficher les félicitations
        self.felicitation_label = tk.Label(self, image=self.felicitation_image)
        # Afficher le premier mode
        self.show_mode1()

    def show_mode1(self) -> None:
        self.felicitation_label.pack_forget()
        self.mode2_frame.pack_forget()
        self.mode1_frame.pack()

    def show_mode2(self) -> None:
        self.felicitation_label.pack_forget()
        self.mode1_frame.pack_forget()
        self.mode2_frame.pack()

    def display_felicitation(self) -> None:
        """Afficher les félicitations."""
        self.felicitation_label.pack()


class Mode1Frame(tk.Frame):
    def __init__(self, master: Jeu, switch_mode_callback: Callable[[], None]) -> None:
        super().__init__(master)
        self.master = master
        self.switch_mode_callback = switch_mode_callback

        label = tk.Label(self, text="Mode 1: Écouter et écrire le chiffre")
        label.pack(pady=10)

        play_sound_button = tk.Button(self, text="Jouer le son", command=self.play_sound)
        play_sound_button.pack(pady=5)

        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)

        check_button = tk.Button(self, text="Vérifier", command=self.check_answer)
        check_button.pack(pady=5)

        next_button = tk.Button(self, text="Suivant", command=self.switch_mode_callback)
        next_button.pack(pady=10)

    def play_sound(self) -> None:
        pygame.mixer.music.load("number.mp3")  # Placez le chemin de votre fichier mp3 ici
        pygame.mixer.music.play()

    def check_answer(self) -> None:
        answer = self.entry.get()

        # Vérifier la réponse (supposons que la bonne réponse est '5' ici)
        if answer == "5":  # Remplacez cela par la logique correcte
            self.master.display_felicitation()
            messagebox.showinfo("Bravo!", "Bonne réponse ! Vous avez gagné un point.")


class Mode2Frame(tk.Frame):
    def __init__(self, master: Jeu, switch_mode_callback: Callable[[], None]) -> None:
        super().__init__(master)
        self.master = master
        self.switch_mode_callback = switch_mode_callback
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
        # Vérifier la réponse (supposons que la bonne réponse est 'pa' ici)
        if syllabe == "pa":  # Remplacez cela par la logique correcte
            self.master.display_felicitation()
            messagebox.showinfo("Bravo!", "Bonne réponse ! Vous avez gagné un point.")


if __name__ == "__main__":
    jeu = Jeu()
    jeu.mainloop()
