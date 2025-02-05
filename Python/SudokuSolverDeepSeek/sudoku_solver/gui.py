import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from sudoku_solver.solver import SudokuSolver
from sudoku_solver.generator import SudokuGenerator
from sudoku_solver.rule_engine import RulesEngine
from sudoku_solver.logger2 import setup_logger
from sudoku_solver.sudoku import (
    SudokuModel,
    SudokuRegion,
    SudokuCell,
    SudokuCellObserver,
)
import json
import os
from typing import List, cast
from common import multilanguage_management
from idlelib import tooltip
import math


class SudokuRegionFrame(tk.Frame):
    # fmt: off
    def __init__(self, region_model:SudokuRegion, master:tk.Frame) -> None:
        super().__init__(master, bd=2, relief="solid")
        # fmt: on
        self._region_model = region_model


class SudokuCellUi(SudokuCellObserver):

    # fmt: off
    def __init__(self, cell_model:SudokuCell, master:tk.Frame) -> None:
        self._text_variable = tk.StringVar()
        self._tk_entry  = tk.Entry(master, width=2,
                    font=("Arial", 18),
                    justify="center",textvariable=self._text_variable)
        # fmt: on
        self._cell_model = cell_model
        tool_tip = tooltip.Hovertip(self._tk_entry, f"x:{cell_model.x}, y:{cell_model.y_from_top}")

    
    @property
    def tk_entry(self) -> tk.Entry:
        return self._tk_entry


    def on_cell_value_updated(self, new_value, cell):
        self._text_variable.set(f"{new_value}")


class SudokuGUI:
    def __init__(self, root: tk.Tk, sudoku_model: SudokuModel) -> None:
        self.root = root
        self._sudoku_model = sudoku_model
        self.root.title("Sudoku Solver x")
        self.generated_board = None
        self.rules_engine = RulesEngine()
        self.logger = setup_logger()
        self._all_cells_ordered_from_top_left: list[list[SudokuCellUi]] = []
        self._region_frames_by_x_and_y_from_top_left: list[list[SudokuRegionFrame]] = []
        self._region_frames_ordered_from_top_left: list[SudokuRegionFrame] = []
        self._translations = multilanguage_management.MultilanguageManagement(
            os.path.join(os.path.dirname(__file__), "../resources/translations.json"),
            "fr",
        )
        self.conflict_display_enabled = tk.BooleanVar(value=False)

        # self.load_translations()
        self.create_widgets()

        self._menubar = tk.Menu(self.root)
        self.create_menu()

    def create_menu(self) -> None:
        """
        Create the menu bar with game options.
        """
        # Game menu
        game_menu = tk.Menu(self._menubar, tearoff=0)

        game_menu.add_command(
            label=self._translations.get_current_language_translation("new_game"),
            command=self.new_game,
        )
        game_menu.add_command(
            label=self._translations.get_current_language_translation("save_game"),
            command=self.save_game,
        )
        game_menu.add_command(
            label=self._translations.get_current_language_translation("load_game"),
            command=self.load_game,
        )
        game_menu.add_command(
            label=self._translations.get_current_language_translation("reset_game"),
            command=self.reset_game,
        )
        game_menu.add_separator()
        game_menu.add_command(
            label=self._translations.get_current_language_translation("exit"),
            command=self.root.quit,
        )
        self._menubar.add_cascade(
            label=self._translations.get_current_language_translation("game"),
            menu=game_menu,
        )

        # Options menu
        options_menu = tk.Menu(self._menubar, tearoff=0)
        options_menu.add_checkbutton(
            label=self._translations.get_current_language_translation(
                "display_conflicts"
            ),
            variable=self.conflict_display_enabled,
            command=self.redraw_conflicts,
        )
        # Language submenu
        language_menu = tk.Menu(options_menu, tearoff=0)
        for lang in self._translations.get_available_languages():
            language_menu.add_command(
                label=lang, command=lambda l=lang: self.change_language(l)
            )
        options_menu.add_cascade(
            label=self._translations.get_current_language_translation("language"),
            menu=language_menu,
        )
        self._menubar.add_cascade(
            label=self._translations.get_current_language_translation("options"),
            menu=options_menu,
        )

        self.root.config(menu=self._menubar)

    def create_widgets(self) -> None:
        # Créer un cadre principal pour contenir toutes les régions
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, padx=10, pady=10)

        grid_frame = tk.Frame(main_frame)
        grid_frame.grid(row=0, column=0, padx=10, pady=10)

        self._region_frames_by_x_and_y_from_top_left = [
            [
                None
                for _ in range(
                    math.isqrt(
                        self._sudoku_model.get_game_board().get_number_of_cells_per_region()
                    )
                )
            ]
            for _ in range(
                math.isqrt(
                    self._sudoku_model.get_game_board().get_number_of_cells_per_region()
                )
            )
        ]

        # Créer les cellules dans chaque région
        self._all_cells_ordered_from_top_left = [
            [
                None
                for _ in range(
                    self._sudoku_model.get_game_board().get_number_of_cells_per_region()
                )
            ]
            for _ in range(
                self._sudoku_model.get_game_board().get_number_of_cells_per_region()
            )
        ]

        # Create all regions
        for region_model in self._sudoku_model.get_game_board().get_all_regions():
            region_frame = SudokuRegionFrame(region_model, grid_frame)
            self._region_frames_by_x_and_y_from_top_left[region_model.x_from_left][
                region_model.y_from_top
            ] = region_frame

            self._region_frames_ordered_from_top_left.append(region_frame)

            region_frame.grid(
                row=region_model.x_from_left,
                column=region_model.y_from_top,
                padx=2,
                pady=2,
            )

            # Create all cells per region
            for cell_model in region_model.get_all_cells_ordered_from_top_left():
                # Créer la cellule dans le cadre de la région correspondante
                cell_ui = SudokuCellUi(cell_model, region_frame)
                self._all_cells_ordered_from_top_left[cell_model.x][
                    cell_model.y_from_top
                ] = cell_ui

                cell_ui.tk_entry.grid(
                    row=cell_model.y_from_top, column=cell_model.x, padx=2, pady=2
                )
                cell_ui.tk_entry.bind("<FocusOut>", self.validate_input)

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

        # Language selector
        self.language_var = tk.StringVar(value="en")
        self.language_label = tk.Label(buttons_frame, text="Language")
        self.language_label.grid(row=1, column=0, pady=10)
        language_selector = ttk.Combobox(
            buttons_frame,
            textvariable=self.language_var,
            values=list(self._translations.get_available_languages()),
        )
        language_selector.grid(row=1, column=1, pady=10)
        language_selector.bind("<<ComboboxSelected>>", self.change_language)

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
                if self._all_cells_ordered_from_top_left[i][j] == cell:
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

    def set_difficulty_and_close(self, popup, difficulty) -> None:
        # Stocker la difficulté sélectionnée et fermer la popup
        self.selected_difficulty = difficulty
        popup.destroy()

    def reset(self) -> None:
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.update_board()

    def update_board(self) -> None:
        for i in range(9):
            for j in range(9):
                self._all_cells_ordered_from_top_left[i][j].delete(0, tk.END)
                if self.board[i][j] != 0:
                    self._all_cells_ordered_from_top_left[i][j].insert(
                        0, str(self.board[i][j])
                    )

    def change_language(
        self, event: tk.Event  # pylint: disable=unused-argument
    ) -> None:  # pylint: disable=unused-argument
        """Change the application language."""
        self.current_language = self.language_var.get()
        self._translations.switch_to_language(self.current_language)
        self._menubar.delete(0, "end")
        self.update_ui_language()

    def update_ui_language(self) -> None:
        """Update the UI with the current language."""
        self.root.title(self._translations.get_current_language_translation("title"))
        self.create_menu()

    def redraw_conflicts(self) -> None:
        """
        Redraw the conflict highlights if enabled.
        """
        # Reset all cell backgrounds for non-fixed cells
        for row in range(9):
            for col in range(9):
                entry = self.cells[row][col]
                if not self.board.fixed[row][col]:
                    entry.config(bg="white")
        if not self.conflict_display_enabled.get():
            return
        # Highlight conflicts in different colors based on rule
        colors = {"row": "#ffcccc", "column": "#ccffcc", "region": "#ccccff"}
        for row in range(9):
            for col in range(9):
                value = self.board.board[row][col]
                if value == 0:
                    continue
                valid, conflicts = check_move(
                    self.board, row, col, value, ignore_current=True
                )
                if not valid:
                    for conflict in conflicts:
                        rule = conflict.get("rule")
                        conflict_row, conflict_col = conflict.get("cell")
                        self.cells[conflict_row][conflict_col].config(
                            bg=colors.get(rule, "yellow")
                        )

    def new_game(self) -> None:
        """
        Start a new game, with a popup to choose difficulty.
        """
        choice = simpledialog.askstring(
            self._translations.translate("new_game"),
            self._translations.translate("choose_difficulty")
            + " (blank, easy, medium, hard):",
            parent=self.root,
        )
        if choice is None:
            return
        choice = choice.lower()
        if choice == "blank":
            self.board = SudokuBoard()
        elif choice in ("easy", "medium", "hard"):
            self.board = generate_puzzle(choice)
        else:
            messagebox.showerror(
                "Error", self._translations.translate("invalid_difficulty")
            )
            return
        self.draw_board()

    def save_game(self) -> None:
        """
        Save the current game state to a file.
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return
        data = {
            "board": self.board.board,
            "fixed": self.board.fixed,
            "language": self.current_language,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        messagebox.showinfo("Info", self._translations.translate("game_saved"))

    def load_game(self) -> None:
        """
        Load a game state from a file.
        """
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.board = SudokuBoard(data["board"], data["fixed"])
        self.current_language = data.get("language", "en")
        self._translations.set_language(self.current_language)
        self.draw_board()
        messagebox.showinfo("Info", self._translations.translate("game_loaded"))

    def reset_game(self) -> None:
        """
        Reset the game by clearing all user entries.
        """
        self.board.clear_user_entries()
        self.draw_board()
