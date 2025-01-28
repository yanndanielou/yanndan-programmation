import tkinter as tk
from tkinter import messagebox
import logging
import src.sudoku_solver.solver

# import solver
# from solver import solve_sudoku

# Configuration des logs avec le nom du fichier et le numéro de ligne
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.create_widgets()

    def create_widgets(self):
        for i in range(9):
            for j in range(9):
                entry = tk.Entry(
                    self.root, width=2, font=("Arial", 18), justify="center"
                )
                entry.grid(row=i, column=j)
                self.cells[i][j] = entry

        solve_button = tk.Button(self.root, text="Solve", command=self.solve)
        solve_button.grid(row=9, column=4, pady=10)

    def solve(self):
        logging.info("Solving Sudoku from GUI")
        board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.cells[i][j].get()
                if value.isdigit() and 1 <= int(value) <= 9:
                    board[i][j] = int(value)
                else:
                    board[i][j] = 0

        if solver.solve_sudoku(board):
            for i in range(9):
                for j in range(9):
                    self.cells[i][j].delete(0, tk.END)
                    self.cells[i][j].insert(0, str(board[i][j]))
            logging.info("Sudoku solved and displayed in GUI")
        else:
            logging.error("No solution exists for the given Sudoku")
            messagebox.showerror("Error", "No solution exists!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
