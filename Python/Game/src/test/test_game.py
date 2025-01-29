# Pytest test cases
import pytest

from game import game


def test_game_board_point() -> None:
    point = game.GenericIntegerGameBoardPoint(2, 3)
    assert point.x == 2
    assert point.y == 3
    assert point.get_short_description() == "GameBoardPoint :[2,3]"


def test_game_board() -> None:
    class IntegerGameBoardPoint(game.GenericIntegerGameBoardPoint):
        def __init__(self, x: int, y: int) -> None:
            super().__init__(x, y)
            pass

    class GameBoard(game.GenericGameBoard):
        def get_total_width(self) -> None:
            return 5

        def get_total_height(self) -> None:
            return 5

        def create_game_board_point(self, x: int, y: int) -> None:
            return IntegerGameBoardPoint(x, y)

    board = GameBoard()
    assert len(board.get_all_game_board_points_as_ordered_list()) == 25
    assert board.get_game_board_point(2, 2) is not None
    assert board.has_neighbour_game_board_point(
        board.get_game_board_point(2, 2), game.NeighbourGameBoardPointDirection.NORTH
    )
