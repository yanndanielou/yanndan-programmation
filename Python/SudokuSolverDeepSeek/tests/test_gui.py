import unittest
from sudoku_solver.gui import SudokuGUI
import tkinter as tk


class TestSudokuGUI(unittest.TestCase):
    def test_gui_creation(self):
        root = tk.Tk()
        app = SudokuGUI(root)
        self.assertIsNotNone(app)


if __name__ == "__main__":
    unittest.main()
