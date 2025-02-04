from dataclasses import dataclass, field
import random
from typing import List, Optional, cast
from sudoku_solver.rule_engine import RulesEngine

import math

from logger import logger_config
from game import game

logger = logger_config.get_logger(__name__)


@dataclass
class SudokuCell(game.GenericIntegerGameBoardPoint):
    _region: Optional["SudokuRegion"] = None
    _value: Optional[int] = None

    @property
    def y_from_top(self) -> int:
        return self.y

    def get_row_number_from_top(self) -> int:
        return self.y

    def get_column_number_from_left(self) -> int:
        return self.x


@dataclass
class SudokuRegion:
    _cells: List[SudokuCell] = field(default_factory=list)
    _x_from_left: int = -1
    _y_from_top: int = -1

    def add_cell(self, cell: SudokuCell) -> None:
        self._cells.append(cell)

    def get_all_cells_ordered_from_top_left(self) -> list[SudokuCell]:
        return self._cells

    @property
    def y_from_top(self) -> int:
        return self._y_from_top

    @property
    def x_from_left(self) -> int:
        return self._x_from_left


@dataclass
class SudokuRowOrColumn:
    _number: int
    _cells: List[SudokuCell] = field(default_factory=list)


class SudokuGameBoard(game.GenericGameBoard):
    def __init__(self, dimension_size: int) -> None:
        super().__init__(total_height=dimension_size, total_width=dimension_size)
        self._dimension_size: int = dimension_size
        self._regions_by_x_and_y: List[List[SudokuRegion]] = []
        self._regions_ordered: List[SudokuRegion] = []

        self.after_constructor()
        self.assign_regions()

    @property
    def dimension_size(self) -> int:
        return self._dimension_size

    @property
    def dimension_size(self) -> int:
        return self._dimension_size

    def get_region_by_x_and_y(self, x: int, y: int) -> SudokuRegion:
        return self._regions_by_x_and_y[x][y]

    def get_all_regions(self) -> list[SudokuRegion]:
        return self._regions_ordered

    def create_game_board_point(self, x: int, y: int) -> SudokuCell:
        return SudokuCell(x, y)

    def assign_regions(self) -> None:
        self._regions_by_x_and_y: List[List[SudokuRegion]] = [
            [SudokuRegion() for _ in range(self._dimension_size)]
            for _ in range(math.isqrt(self._dimension_size))
        ]
        for i in range(math.isqrt(self._dimension_size)):
            for j in range(math.isqrt(self._dimension_size)):
                region = self._regions_by_x_and_y[i][j]
                region._x_from_left = i
                region._y_from_top = j
                self._regions_ordered.append(region)

        for cell in self.get_all_game_board_points_as_ordered_list():
            cell_row_number_from_top = cast(
                "SudokuCell", cell
            ).get_row_number_from_top()
            cell_column = cast("SudokuCell", cell).x

            cell_region_row = cell_row_number_from_top // math.isqrt(
                self._dimension_size
            )
            cell_region_col = cell_column // math.isqrt(self._dimension_size)

            cell_region: SudokuRegion = self._regions_by_x_and_y[cell_region_col][
                cell_region_row
            ]

            cell_region.add_cell(cell)


class SudokuModel:
    """Represents a Sudoku puzzle and provides methods to solve it."""

    def __init__(self, dimension_size: int) -> None:

        self._game_board: SudokuGameBoard = SudokuGameBoard(dimension_size)
        # self.grid = grid if grid else self.generate_empty_grid()

        self.rule_engine = RulesEngine()

    def get_game_board(self) -> SudokuGameBoard:
        return self._game_board

    def solve_grid(self, grid: List[List[Optional[int]]]) -> bool:
        """Solve a Sudoku grid using backtracking."""
        for row in range(9):
            for col in range(9):
                if grid[row][col] is None:
                    for num in random.sample(range(1, 10), 9):  # Randomize numbers
                        if RulesEngine.is_valid_move(grid, row, col, num):
                            grid[row][col] = num
                            if self.solve_grid(grid):
                                return True
                            grid[row][col] = None
                    return False
        return True

    def generate_puzzle(self, difficulty: str) -> List[List[Optional[int]]]:
        """Generate a Sudoku puzzle with a given difficulty."""
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

        return grid
