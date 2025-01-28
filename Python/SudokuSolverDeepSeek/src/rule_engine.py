from typing import List, Optional


class RuleEngine:
    """Engine to enforce Sudoku rules."""

    def is_valid_move(
        self, grid: List[List[Optional[int]]], row: int, col: int, num: int
    ) -> bool:
        """Check if a move is valid according to Sudoku rules."""
        # Check row
        if num in grid[row]:
            return False

        # Check column
        if num in [grid[i][col] for i in range(9)]:
            return False

        # Check 3x3 region
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if grid[start_row + i][start_col + j] == num:
                    return False

        return True
