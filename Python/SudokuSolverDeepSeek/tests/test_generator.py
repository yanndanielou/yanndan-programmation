import unittest
from sudoku_solver.generator import SudokuGenerator


class TestSudokuGenerator(unittest.TestCase):
    def test_generate(self):
        generator = SudokuGenerator()
        board = generator.generate("easy")
        self.assertEqual(len(board), 9)
        for row in board:
            self.assertEqual(len(row), 9)


if __name__ == "__main__":
    unittest.main()
