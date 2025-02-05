from sudoku_solver.difficulties import GameSize, PuzzleDifficulty

PUZZLE_DIFFICULTY_LEVELS = [
    PuzzleDifficulty("Very easy", 90),
    PuzzleDifficulty("easy", 80),
    PuzzleDifficulty("medium", 50),
    PuzzleDifficulty("hard", 30),
    PuzzleDifficulty("Few cells forced", 2),
]

SUDOKU_BEGINNERS_SIZE: GameSize = GameSize(
    _name="SUDOKU_BEGINNERS_SIZE",
    allowed_values_in_cells=[str(i) for i in range(1, 3)],  # list(str(range(1, 3)))
)
SUDOKU_NORMAL_SIZE: GameSize = GameSize(
    _name="SUDOKU_BEGINNERS_SIZE",
    allowed_values_in_cells=[str(i) for i in range(1, 10)],
)
