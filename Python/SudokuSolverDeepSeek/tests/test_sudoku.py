import pytest
from sudoku_solver import sudoku


class TestSudokuConstruction:

    def test_few_regions(self) -> None:
        sudoku_test: sudoku.SudokuModel = sudoku.SudokuModel()
        game_board = sudoku_test.get_game_board()

        first_region: sudoku.SudokuRegion = game_board.get_region_by_x_and_y(0, 0)
        assert first_region._cells[0].x == 0
        assert first_region._cells[0].y == 0

        region: sudoku.SudokuRegion = game_board.get_region_by_x_and_y(1, 0)
        assert region.get_all_cells_ordered()[0].x == 3
        assert region.get_all_cells_ordered()[0].y == 0

        region = game_board.get_region_by_x_and_y(0, 1)
        assert region.get_all_cells_ordered()[0].x == 0
        assert region.get_all_cells_ordered()[0].y == 3

        @pytest.mark.parametrize(
            "total_height_tested,total_width_tested,expected_points_number",
            [
                (1, 1, 1),
                (1, 2, 2),
                (2, 1, 2),
                (2, 2, 4),
                (3, 5, 15),
                (5, 3, 15),
                (5, 5, 25),
            ],
        )
        def test_regions(self) -> None:
            sudoku_test: sudoku.SudokuModel = sudoku.SudokuModel()
            game_board = sudoku_test.get_game_board()
