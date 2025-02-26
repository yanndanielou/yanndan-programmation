import random
from typing import List, Optional
from rule_engine import RuleEngine

from logger import logger_config

logger = logger_config.get_logger(__name__)


class Sudoku:
    """Represents a Sudoku puzzle and provides methods to solve it."""

    def __init__(self, grid: Optional[List[List[Optional[int]]]] = None):
        self.grid = grid if grid else self.generate_full_grid()
        self.rule_engine = RuleEngine()

    def generate_full_grid(self) -> List[List[Optional[int]]]:
        """Generate a fully solved Sudoku grid."""
        grid = [[None for _ in range(9)] for _ in range(9)]
        print(f"Grid before generate_full_grid: {grid}")

        self.solve_grid(grid)
        print(f"Grid at the end of generate_full_grid: {grid}")

        return grid

    def solve_grid(self, grid: List[List[Optional[int]]]) -> bool:
        """Solve a Sudoku grid using backtracking."""
        for row in range(9):
            for col in range(9):
                if grid[row][col] is None:
                    for num in random.sample(range(1, 10), 9):  # Randomize numbers
                        if RuleEngine.is_valid_move(grid, row, col, num):
                            grid[row][col] = num
                            if self.solve_grid(grid):
                                return True
                            grid[row][col] = None
                    return False
        return True

    def generate_puzzle(self, difficulty: str) -> List[List[Optional[int]]]:
        """Generate a Sudoku puzzle with a given difficulty."""
        print(f"Grid before generate_puzzle: {grid}")

        grid = [row[:] for row in self.grid]  # Copy the solved grid
        empty_cells = 0

        if difficulty == "easy":
            empty_cells = 30
        elif difficulty == "medium":
            empty_cells = 45
        elif difficulty == "hard":
            empty_cells = 60

        cells = [(row, col) for row in range(9) for col in range(9)]
        random.shuffle(cells)

        for row, col in cells[:empty_cells]:
            grid[row][col] = None

        print(f"Grid at the end of generate_puzzle: {grid}")

        return grid

    def is_valid(self, row: int, col: int, num: int) -> bool:
        """Check if placing a number in a cell is valid."""
        logger.debug(f"Checking validity of {num} at ({row}, {col})")
        return self.rule_engine.is_valid_move(self.grid, row, col, num)

    def solve(self) -> bool:
        """Solve the Sudoku puzzle using backtracking."""
        return self.solve_grid(self.grid)

    def get_grid(self) -> List[List[Optional[int]]]:
        """Return the current state of the grid."""
        return self.grid
