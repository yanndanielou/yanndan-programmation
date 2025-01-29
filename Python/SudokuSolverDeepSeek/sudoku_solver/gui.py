import tkinter as tk
from tkinter import messagebox, simpledialog
from solver import SudokuSolver
from generator import SudokuGenerator
from rule_engine import RulesEngine
from logger2 import setup_logger
import json
import os


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver x")
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.generated_board = None
        self.rules_engine = RulesEngine()
        self.logger = setup_logger()
        self.load_translations()
        self.create_widgets()

    def load_translations(self):
        with open(
            os.path.join(os.path.dirname(__file__), "translations.json"), "r"
        ) as f:
            self.translations = json.load(f)

    def create_widgets(self) -> None:
        # Créer un cadre principal pour contenir toutes les régions
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, padx=10, pady=10)

        grid_frame = tk.Frame(main_frame)
        grid_frame.grid(row=0, column=0, padx=10, pady=10)

        # Créer des cadres pour chaque région 3x3
        self.region_frames = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                # Créer un cadre pour la région (i, j)
                self.region_frames[i][j] = tk.Frame(grid_frame, bd=2, relief="solid")
                self.region_frames[i][j].grid(row=i, column=j, padx=2, pady=2)

        # Créer les cellules dans chaque région
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                # Calculer la position de la région et de la cellule dans la région
                region_row, region_col = i // 3, j // 3
                cell_row, cell_col = i % 3, j % 3

                # Créer la cellule dans le cadre de la région correspondante
                self.cells[i][j] = tk.Entry(
                    self.region_frames[region_row][region_col],
                    width=2,
                    font=("Arial", 18),
                    justify="center",
                )
                self.cells[i][j].grid(row=cell_row, column=cell_col, padx=2, pady=2)
                self.cells[i][j].bind("<FocusOut>", self.validate_input)

        buttons_frame = tk.Frame(main_frame)
        buttons_frame.grid(row=1, column=0, padx=10, pady=10)

        # Ajouter les boutons en dessous de la grille
        self.solve_button = tk.Button(buttons_frame, text="Solve", command=self.solve)
        self.solve_button.grid(row=0, column=0, padx=10, pady=10)

        self.generate_button = tk.Button(
            buttons_frame, text="Generate", command=self.generate
        )
        self.generate_button.grid(row=0, column=1, padx=10, pady=10)

        self.reset_button = tk.Button(buttons_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=2, padx=10, pady=10)

    def validate_input(self, event):
        # Récupérer la cellule qui a déclenché l'événement
        cell = event.widget
        row, col = self.get_cell_position(cell)

        # Récupérer la valeur entrée par l'utilisateur
        value = cell.get().strip()

        # Si la cellule est vide, la valeur est valide
        if not value:
            return

        # Vérifier si la valeur est un chiffre entre 1 et 9
        if not value.isdigit() or int(value) < 1 or int(value) > 9:
            messagebox.showerror(
                "Invalid Input", "Please enter a number between 1 and 9."
            )
            cell.delete(0, tk.END)
            return

        # Convertir la valeur en entier
        value = int(value)

        # Vérifier si la valeur est valide selon les règles du Sudoku
        if not self.rules_engine.validate_move(self.board, row, col, value):
            # Trouver les cases en conflit
            conflicts = self.find_conflicts(row, col, value)

            # Afficher un message d'erreur avec les cases en conflit
            conflict_message = self.generate_conflict_message(conflicts)
            messagebox.showerror(
                "Invalid Move",
                f"The value {value} conflicts with the following cells:\n{conflict_message}",
            )

            # Laisser l'utilisateur choisir de conserver ou de corriger la valeur
            keep_value = messagebox.askyesno(
                "Keep Value?", "Do you want to keep this value anyway?"
            )
            if not keep_value:
                cell.delete(0, tk.END)
            return

        # Mettre à jour la grille avec la nouvelle valeur
        self.board[row][col] = value

    def get_cell_position(self, cell):
        """
        Retourne la position (ligne, colonne) d'une cellule dans la grille.
        """
        for i in range(9):
            for j in range(9):
                if self.cells[i][j] == cell:
                    return i, j
        return None, None

    def find_conflicts(self, row, col, value):
        """
        Trouve toutes les cases en conflit avec la valeur donnée.
        """
        conflicts = []

        # Vérifier les conflits dans la ligne
        for i in range(9):
            if self.board[row][i] == value and i != col:
                conflicts.append((row, i, "row"))

        # Vérifier les conflits dans la colonne
        for i in range(9):
            if self.board[i][col] == value and i != row:
                conflicts.append((i, col, "column"))

        # Vérifier les conflits dans la région 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.board[start_row + i][start_col + j] == value and (
                    start_row + i != row or start_col + j != col
                ):
                    conflicts.append((start_row + i, start_col + j, "region"))

        return conflicts

    def generate_conflict_message(self, conflicts):
        """
        Génère un message détaillant les cases en conflit.
        """
        message = ""
        for conflict in conflicts:
            row, col, conflict_type = conflict
            message += f"- Cell ({row + 1}, {col + 1}) in the {conflict_type}\n"
        return message

    def solve(self):
        solver = SudokuSolver(self.board)
        if solver.solve():
            self.update_board()
        else:
            messagebox.showerror("Error", "No solution exists")

    def generate(self):
        # Afficher une popup pour sélectionner la difficulté
        difficulty = self.select_difficulty()
        if difficulty:
            generator = SudokuGenerator()
            self.generated_board = generator.generate(difficulty)
            self.update_board()

    def select_difficulty(self):
        # Créer une popup pour sélectionner la difficulté
        difficulty_popup = tk.Toplevel(self.root)
        difficulty_popup.title("Select Difficulty")
        difficulty_popup.geometry("300x150")

        # Ajouter des boutons pour chaque niveau de difficulté
        easy_button = tk.Button(
            difficulty_popup,
            text="Easy",
            command=lambda: self.set_difficulty_and_close(difficulty_popup, "easy"),
        )
        easy_button.pack(pady=10)

        medium_button = tk.Button(
            difficulty_popup,
            text="Medium",
            command=lambda: self.set_difficulty_and_close(difficulty_popup, "medium"),
        )
        medium_button.pack(pady=10)

        hard_button = tk.Button(
            difficulty_popup,
            text="Hard",
            command=lambda: self.set_difficulty_and_close(difficulty_popup, "hard"),
        )
        hard_button.pack(pady=10)

        # Variable pour stocker la difficulté sélectionnée
        self.selected_difficulty = None

        # Attendre que l'utilisateur fasse un choix
        difficulty_popup.wait_window()

        return self.selected_difficulty

    def set_difficulty_and_close(self, popup, difficulty):
        # Stocker la difficulté sélectionnée et fermer la popup
        self.selected_difficulty = difficulty
        popup.destroy()

    def reset(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.update_board()

    def update_board(self):
        for i in range(9):
            for j in range(9):
                self.cells[i][j].delete(0, tk.END)
                if self.board[i][j] != 0:
                    self.cells[i][j].insert(0, str(self.board[i][j]))
