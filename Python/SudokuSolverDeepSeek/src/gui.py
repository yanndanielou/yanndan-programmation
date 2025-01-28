import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from typing import List, Optional, Dict
import json
import os
from sudoku import Sudoku

from logger import logger_config

logger = logger_config.get_logger(__name__)


class SudokuGUI:
    """Graphical User Interface for the Sudoku solver."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.translations = self.load_translations()
        self.current_language = "en"  # Default language
        self.sudoku = Sudoku()
        self.create_widgets()
        self.update_ui_language()

    def load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translations from the JSON file."""
        translations_path = os.path.join(os.path.dirname(__file__), "translations.json")
        try:
            with open(translations_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            logger.error("Translations file not found.")
            return {}
        except json.JSONDecodeError:
            logger.error("Invalid translations file.")
            return {}

    def translate(self, key: str) -> str:
        """Get the translation for a given key in the current language."""
        return self.translations.get(key, {}).get(self.current_language, key)

    def update_ui_language(self):
        """Update the UI with the current language."""
        self.root.title(self.translate("title"))
        self.solve_button.config(text=self.translate("solve_button"))
        self.clear_button.config(text=self.translate("clear_button"))
        self.language_label.config(text=self.translate("language_label"))
        self.difficulty_label.config(text=self.translate("difficulty_label"))
        self.save_button.config(text=self.translate("save_button"))
        self.load_button.config(text=self.translate("load_button"))

    def create_widgets(self):
        """Create the Sudoku grid, buttons, number selector, and language selector."""
        # Sudoku grid
        self.cells: List[List[tk.Entry]] = []
        for row in range(9):
            row_cells = []
            for col in range(9):
                cell = tk.Entry(
                    self.root, width=3, font=("Arial", 18), justify="center"
                )
                cell.grid(row=row, column=col, padx=1, pady=1)
                cell.bind("<FocusOut>", self.validate_cell)
                row_cells.append(cell)
            self.cells.append(row_cells)

        # Number selector
        self.number_var = tk.StringVar(value="1")
        number_selector = ttk.Combobox(
            self.root,
            textvariable=self.number_var,
            values=[str(i) for i in range(1, 10)],
        )
        number_selector.grid(row=9, column=0, columnspan=3, pady=10)
        number_selector.bind("<<ComboboxSelected>>", self.highlight_number)

        # Buttons
        self.solve_button = tk.Button(self.root, text="Solve", command=self.solve)
        self.solve_button.grid(row=9, column=4, pady=10)

        self.clear_button = tk.Button(
            self.root, text="Clear Highlights", command=self.clear_highlights
        )
        self.clear_button.grid(row=9, column=5, pady=10)

        # Language selector
        self.language_var = tk.StringVar(value="en")
        self.language_label = tk.Label(self.root, text="Language")
        self.language_label.grid(row=10, column=0, pady=10)
        language_selector = ttk.Combobox(
            self.root,
            textvariable=self.language_var,
            values=list(self.get_available_languages()),
        )
        language_selector.grid(row=10, column=1, pady=10)
        language_selector.bind("<<ComboboxSelected>>", self.change_language)

        # Difficulty selector
        self.difficulty_var = tk.StringVar(value="easy")
        self.difficulty_label = tk.Label(self.root, text="Difficulty")
        self.difficulty_label.grid(row=11, column=0, pady=10)
        difficulty_selector = ttk.Combobox(
            self.root,
            textvariable=self.difficulty_var,
            values=["easy", "medium", "hard"],
        )
        difficulty_selector.grid(row=11, column=1, pady=10)
        difficulty_selector.bind("<<ComboboxSelected>>", self.generate_puzzle)

        # Save and load buttons
        self.save_button = tk.Button(self.root, text="Save", command=self.save_game)
        self.save_button.grid(row=12, column=0, pady=10)

        self.load_button = tk.Button(self.root, text="Load", command=self.load_game)
        self.load_button.grid(row=12, column=1, pady=10)

    def get_available_languages(self) -> List[str]:
        """Get the list of available languages from the translations file."""
        if not self.translations:
            return ["en"]  # Default to English if no translations are loaded
        # Get the languages from the first key (assuming all keys have the same languages)
        first_key = next(iter(self.translations))
        return list(self.translations[first_key].keys())

    def change_language(self, event):
        """Change the application language."""
        self.current_language = self.language_var.get()
        self.update_ui_language()

    def generate_puzzle(self, event=None):
        """Generate a new Sudoku puzzle based on the selected difficulty."""
        difficulty = self.difficulty_var.get()
        puzzle = self.sudoku.generate_puzzle(difficulty)
        self.update_grid(puzzle)

    def save_game(self):
        """Save the current game to a file."""
        file_path = filedialog.asksaveasfilename(
            initialdir=".",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if file_path:
            grid = self.get_grid()
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(grid, file)
            messagebox.showinfo("Save", "Game saved successfully!")

    def load_game(self):
        """Load a game from a file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                grid = json.load(file)
            self.update_grid(grid)
            messagebox.showinfo("Load", "Game loaded successfully!")

    def validate_cell(self, event):
        """Validate the cell value and show an error if invalid."""
        widget = event.widget
        row, col = self.get_cell_position(widget)
        value = widget.get()

        if value:
            try:
                num = int(value)
                if num < 1 or num > 9:
                    raise ValueError(self.translate("invalid_value"))
            except ValueError as e:
                self.show_error(row, col, str(e))
                return

            grid = self.get_grid()
            sudoku = Sudoku(grid)
            if not sudoku.is_valid(row, col, num):
                self.show_error(row, col, self.translate("invalid_move"))
                return

    def show_error(self, row: int, col: int, message: str):
        """Show an error message and highlight conflicting cells."""
        response = messagebox.askyesno(
            "Invalid Input",
            f"{message}\n{self.translate('keep_value_prompt')}",
        )
        if not response:
            self.cells[row][col].delete(0, tk.END)
        else:
            self.highlight_conflicts(row, col)

    def highlight_conflicts(self, row: int, col: int):
        """Highlight cells that conflict with the given cell."""
        num = int(self.cells[row][col].get())
        grid = self.get_grid()
        sudoku = Sudoku(grid)

        for r in range(9):
            for c in range(9):
                if (r == row and c == col) or grid[r][c] != num:
                    continue
                if not sudoku.is_valid(r, c, num):
                    self.cells[r][c].config(bg="red")

    def highlight_number(self, event):
        """Highlight all occurrences of the selected number."""
        self.clear_highlights()
        num = int(self.number_var.get())
        for row in range(9):
            for col in range(9):
                if self.cells[row][col].get() == str(num):
                    self.cells[row][col].config(bg="yellow")

    def clear_highlights(self):
        """Clear all highlights in the grid."""
        for row in range(9):
            for col in range(9):
                self.cells[row][col].config(bg="white")

    def get_cell_position(self, widget: tk.Widget) -> tuple[int, int]:
        """Get the row and column of a cell widget."""
        for row in range(9):
            for col in range(9):
                if self.cells[row][col] == widget:
                    return row, col
        return -1, -1

    def solve(self):
        """Solve the Sudoku puzzle and update the GUI."""
        grid = self.get_grid()
        sudoku = Sudoku(grid)
        if sudoku.solve():
            self.update_grid(sudoku.get_grid())
        else:
            messagebox.showerror("Error", self.translate("no_solution"))

    def get_grid(self) -> List[List[Optional[int]]]:
        """Extract the grid from the GUI."""
        grid = []
        for row in range(9):
            grid_row = []
            for col in range(9):
                value = self.cells[row][col].get()
                grid_row.append(int(value) if value else None)
            grid.append(grid_row)
        return grid

    def update_grid(self, grid: List[List[Optional[int]]]):
        """Update the GUI with the solved grid."""
        for row in range(9):
            for col in range(9):
                self.cells[row][col].delete(0, tk.END)
                if grid[row][col] is not None:
                    self.cells[row][col].insert(0, str(grid[row][col]))


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
