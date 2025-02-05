from sudoku_solver.difficulties import GameSize

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

SUDOKU_BEGINNERS_SIZE: GameSize = GameSize(
    _name="SUDOKU_BEGINNERS_SIZE",
    allowed_values_in_cells=[str(i) for i in range(1, 3)],  # list(str(range(1, 3)))
)
SUDOKU_NORMAL_SIZE: GameSize = GameSize(
    _name="SUDOKU_BEGINNERS_SIZE",
    allowed_values_in_cells=[str(i) for i in range(1, 10)],
)
