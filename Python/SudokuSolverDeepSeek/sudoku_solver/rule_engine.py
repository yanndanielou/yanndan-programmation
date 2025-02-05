from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sudoku_solver.sudoku import SudokuModel


class RulesEngine:
    def __init__(self) -> None:
        pass

    def is_valid_move(self, model: "SudokuModel", row: int, col: int, num: int) -> bool:
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

    def validate_move(self, board, row: int, col: int, num: int) -> None:
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False

        return True
