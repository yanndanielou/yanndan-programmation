from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sudoku_solver.sudoku import SudokuCell, SudokuModel
    from sudoku_solver.gui import SudokuGUI


@dataclass
class SudokuController:
    sudoku_model: "SudokuModel"
    sudoku_ui: "SudokuGUI"

    def update_cell_content_by_user(
        self, cell_model: "SudokuCell", new_value: str
    ) -> None:
        cell_model.update_cell_content_by_user(new_value)
