from sudoku_solver.gui import SudokuGUI
from sudoku_solver import sudoku
from sudoku_solver import constants
import tkinter as tk


def main() -> None:
    root = tk.Tk()
    model = sudoku.SudokuModel(constants.SUDOKU_NORMAL_SIZE)
    app = SudokuGUI(root, model)
    root.mainloop()


if __name__ == "__main__":
    main()
