import random
from typing import List
from sudoku_solver.solver import SudokuSolver


class SudokuGenerator:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def generate(self, difficulty: str) -> List[List[int]]:
        self.solve()
        self.remove_numbers(difficulty)
        return self.board

    def solve(self):
        solver = SudokuSolver(self.board)
        solver.solve()

    def remove_numbers(self, difficulty: str):
        levels = {"easy": 30, "medium": 40, "hard": 50}
        to_remove = levels.get(difficulty, 30)

        for _ in range(to_remove):
            row, col = random.randint(0, 8), random.randint(0, 8)
            while self.board[row][col] == 0:
                row, col = random.randint(0, 8), random.randint(0, 8)
            self.board[row][col] = 0
