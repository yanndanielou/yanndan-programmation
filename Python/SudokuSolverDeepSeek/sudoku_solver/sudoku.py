from dataclasses import dataclass, field
import random
from typing import List, Optional, cast
from sudoku_solver.rule_engine import RulesEngine

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
    def __init__(self, width: int = 9, height: int = 9) -> None:
        super().__init__(total_height=height, total_width=width)
        self._regions_by_x_and_y: List[List[SudokuRegion]] = []
        self._regions_ordered: List[SudokuRegion] = []

        self.after_constructor()
        self.assign_regions()

    def get_region_by_x_and_y(self, x: int, y: int) -> SudokuRegion:
        return self._regions_by_x_and_y[x][y]

    def get_all_regions(self) -> list[SudokuRegion]:
        return self._regions_ordered

    def create_game_board_point(self, x: int, y: int) -> SudokuCell:
        return SudokuCell(x, y)

    def assign_regions(self) -> None:
        self._regions_by_x_and_y: List[List[SudokuRegion]] = [
            [SudokuRegion() for _ in range(3)] for _ in range(3)
        ]
        for i in range(3):
            for j in range(3):
                region = self._regions_by_x_and_y[i][j]
                region._x_from_left = i
                region._y_from_top = j
                self._regions_ordered.append(region)

        for cell in self.get_all_game_board_points_as_ordered_list():
            cell_row_number_from_top = cast(
                "SudokuCell", cell
            ).get_row_number_from_top()
            cell_column = cast("SudokuCell", cell).x

            cell_region_row = cell_row_number_from_top // 3
            cell_region_col = cell_column // 3

            cell_region: SudokuRegion = self._regions_by_x_and_y[cell_region_col][
                cell_region_row
            ]

            cell_region.add_cell(cell)


class SudokuModel:
    """Represents a Sudoku puzzle and provides methods to solve it."""

    def __init__(self) -> None:

        self._game_board: SudokuGameBoard = SudokuGameBoard()
        # self.grid = grid if grid else self.generate_empty_grid()

        """self._columns: List[SudokuRowOrColumn] = []
        for _ in range(3):
            self._columns.append(SudokuRowOrColumn(_))

        self._rows: List[SudokuRowOrColumn] = []
        for _ in range(3):
            self._rows.append(SudokuRowOrColumn(_))"""

        """         # Créer les cellules dans chaque région
        self._cells_by_row_and_column: List[List[SudokuCell | None]] = [
            [None for _ in range(9)] for _ in range(9)
        ]
        for i in range(9):
            for j in range(9):
                # Calculer la position de la région et de la cellule dans la région
                region_row, region_col = i // 3, j // 3
                cell_row, cell_col = i % 3, j % 3

                # Créer la cellule dans le cadre de la région correspondante
                self._cells_by_row_and_column[i][j] = SudokuCell(
                    _region=self._regions[region_row][region_col],
                    _column=self._columns[cell_col],
                    _row=self._rows[cell_row],
                ) """

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
