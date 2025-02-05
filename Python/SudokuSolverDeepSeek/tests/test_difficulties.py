from sudoku_solver import difficulties


class TestGameSize:
    def test_generate(self) -> None:
        game_size = difficulties.GameSize("kid", [1, 2])
        assert game_size is not None
