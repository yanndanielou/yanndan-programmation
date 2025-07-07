import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from PIL import ImageTk, Image
import pygame
from typing import Callable


class Jeu(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

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

        self.mode1_frame = Mode1Frame(self, self.show_mode2)
        self.mode2_frame = Mode2Frame(self, self.show_mode1)

        # Afficher le premier mode
        self.show_mode1()

    def prompt_for_name(self) -> None:
        """Demande le prénom de l'enfant au démarrage."""
        self.child_name = simpledialog.askstring("Bienvenue", "Entrez votre prénom :")
        if not self.child_name:  # Si aucune entrée, on utilise un nom par défaut
            self.child_name = "Enfant"

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

    def display_felicitation_dialog(self) -> None:
        """Afficher une fenêtre popup personnalisée de félicitations."""
        popup = Toplevel(self)
        popup.title("Bravo!")
        popup.geometry("300x300")

        felicitation_label = tk.Label(popup, image=self.felicitation_image)
        felicitation_label.pack(pady=10)

        message_label = tk.Label(popup, text="Bonne réponse ! Vous avez gagné un point.", font=("Arial", 12))
        message_label.pack(pady=10)

        # Fermer le popup automatiquement après 15 secondes ou à l'appui sur "Entrée"
        popup.after(15000, popup.destroy)
        popup.bind("<Return>", lambda _: popup.destroy())


class HeaderFrame(tk.Frame):
    def __init__(self, master: Jeu) -> None:
        super().__init__(master, bg="lightblue")
        self.name_label = tk.Label(self, text="", bg="lightblue", font=("Arial", 14, "bold"))
        self.name_label.pack(side=tk.LEFT, padx=10)
        self.points_label = tk.Label(self, text="", bg="lightblue", font=("Arial", 14, "bold"))
        self.points_label.pack(side=tk.RIGHT, padx=10)
        self.update_info(master.child_name, master.points)

    def update_info(self, name: str, points: int) -> None:
        self.name_label.config(text=f"Prénom: {name}")
        self.points_label.config(text=f"Points: {points}")


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
        self.entry.bind("<Return>", lambda _: self.check_answer())  # Associer la touche "Entrée" à la validation

        check_button = tk.Button(self, text="Vérifier", command=self.check_answer)
        check_button.pack(pady=5)

        next_button = tk.Button(self, text="Suivant", command=self.switch_mode_callback)
        next_button.pack(pady=10)

    def play_sound(self) -> None:
        pygame.mixer.music.load("number.mp3")  # Placez le chemin de votre fichier mp3 ici
        pygame.mixer.music.play()

    def check_answer(self) -> None:
        answer = self.entry.get()
        correct_answer = "5"  # Remplacez cela par la logique correcte

        if answer == correct_answer:
            self.master.points += 1
            self.master.update_header()
            self.master.display_felicitation_dialog()


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
        correct_syllabe = "pa"  # Remplacez cela par la logique correcte
        if syllabe == correct_syllabe:
            self.master.points += 1
            self.master.update_header()
            self.master.display_felicitation_dialog()


if __name__ == "__main__":
    jeu = Jeu()
    jeu.mainloop()
