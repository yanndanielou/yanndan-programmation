import pytest
from src.sudoku_solver import rule_engine


class TestRuleEngine:
    def test_is_valid_move(self) -> None:
        grid = [
            [5, 3, None, None, 7, None, None, None, None],
            [6, None, None, 1, 9, 5, None, None, None],
            [None, 9, 8, None, None, None, None, 6, None],
            [8, None, None, None, 6, None, None, None, 3],
            [4, None, None, 8, None, 3, None, None, 1],
            [7, None, None, None, 2, None, None, None, 6],
            [None, 6, None, None, None, None, 2, 8, None],
            [None, None, None, 4, 1, 9, None, None, 5],
            [None, None, None, None, 8, None, None, 7, 9],
        ]
        engine = rule_engine.RuleEngine()
        assert engine.is_valid_move(grid, 0, 2, 4)
        assert not engine.is_valid_move(grid, 0, 2, 5)
