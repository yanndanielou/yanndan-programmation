from dataclasses import dataclass, field
import random
from typing import List, Optional, cast
from sudoku_solver.rule_engine import RulesEngine
from sudoku_solver.difficulties import GameSize
from sudoku_solver.logger_sudoku import get_logger

import math

from logger import logger_config
from game import game
from abc import ABC, abstractmethod


logger = get_logger(__name__)


class SudokuCellObserver(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def on_cell_value_updated(self, new_value: str, cell: "SudokuCell") -> None:
        pass


@dataclass
class SudokuCell(game.GenericIntegerGameBoardPoint):
    _region: Optional["SudokuRegion"] = None
    _value: Optional[str] = None
    _observers: List[SudokuCellObserver] = field(default_factory=list)
    _enforcedValueByPuzzle = False
    _found_by_software_solver = False
    _entered_by_user = False

    @property
    def y_from_top(self) -> int:
        return self.y

    @property
    def enforcedValueByPuzzle(self) -> bool:
        return self._enforcedValueByPuzzle

    def update_cell_content_by_user(self, new_value: str) -> None:
        self._value = new_value
        self._entered_by_user = True
        logger.info(f"update_cell_content_by_user {new_value} at ({self.x}, {self.y})")

    def get_row_number_from_top(self) -> int:
        return self.y

    def get_column_number_from_left(self) -> int:
        return self.x

    def attach(self, observer: SudokuCellObserver) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: SudokuCellObserver) -> None:
        self._observers.remove(observer)

    def notify_value_changed(self) -> None:
        for observer in self._observers:
            observer.on_cell_value_updated(new_value=self._value, cell=self)


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
    def __init__(self, game_size: GameSize) -> None:
        super().__init__(
            total_height=game_size.get_number_of_cells_per_region(),
            total_width=game_size.get_number_of_cells_per_region(),
        )
        self._game_size: GameSize = game_size
        self._regions_by_x_and_y: List[List[SudokuRegion]] = []
        self._regions_ordered: List[SudokuRegion] = []

        self._columns: List[SudokuRowOrColumn] = []
        self._rows_from_top: List[SudokuRowOrColumn] = []

        self.after_constructor()
        self.assign_regions()
        self.assign_rows_and_columns()

    def assign_rows_and_columns(self) -> None:
        for cell in self.get_all_game_board_points_as_ordered_list():

            pass

    def get_number_of_cells_per_region(self) -> int:
        return self._game_size.get_number_of_cells_per_region()

    def get_region_height_width(self) -> int:
        return self._game_size.get_region_height()

    def get_region_by_x_and_y(self, x: int, y: int) -> SudokuRegion:
        return self._regions_by_x_and_y[x][y]

    def get_all_regions(self) -> list[SudokuRegion]:
        return self._regions_ordered

    def create_game_board_point(self, x: int, y: int) -> SudokuCell:
        return SudokuCell(x, y)

    def assign_regions(self) -> None:
        self._regions_by_x_and_y: List[List[SudokuRegion]] = [
            [SudokuRegion() for _ in range(self.get_number_of_cells_per_region())]
            for _ in range(self.get_region_height_width())
        ]
        for i in range(self.get_region_height_width()):
            for j in range(self.get_region_height_width()):
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
                self.get_number_of_cells_per_region()
            )
            cell_region_col = cell_column // self.get_region_height_width()

            cell_region: SudokuRegion = self._regions_by_x_and_y[cell_region_col][
                cell_region_row
            ]

            cell_region.add_cell(cell)


class SudokuModel:
    """Represents a Sudoku puzzle and provides methods to solve it."""

    def __init__(self, game_size: GameSize) -> None:

        self._game_board: SudokuGameBoard = SudokuGameBoard(game_size)
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
