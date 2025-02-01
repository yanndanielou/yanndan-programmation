# Pytest test cases
import pytest

from game import game


class TestGenericIntegerGameBoardPoint:

    def test_game_board_point(self) -> None:
        point = game.GenericIntegerGameBoardPoint(2, 3)
        assert point.x == 2
        assert point.y == 3
        assert point.get_short_description() == "GameBoardPoint :[2,3]"


class IntegerGameBoardPoint(game.GenericIntegerGameBoardPoint):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        pass


class GameBoard(game.GenericGameBoard):

    def create_game_board_point(self, x: int, y: int) -> "IntegerGameBoardPoint":
        return IntegerGameBoardPoint(x, y)


class TestGameBoard:
    def test_board_creation(self) -> None:
        board = GameBoard(total_height=5, total_width=3)
        board.after_constructor()
        assert board is not None

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
    def test_points_creation_param(
        self,
        total_height_tested: int,
        total_width_tested: int,
        expected_points_number: int,
    ) -> None:
        board = GameBoard(
            total_height=total_height_tested, total_width=total_width_tested
        )
        board.after_constructor()
        assert (
            len(board.get_all_game_board_points_as_ordered_list())
            == expected_points_number
        )

    def test_points_creation_1(self) -> None:
        board = GameBoard(total_height=1, total_width=1)
        board.after_constructor()
        assert len(board.get_all_game_board_points_as_ordered_list()) == 1

    def test_points_creation_4(self) -> None:
        board = GameBoard(total_height=2, total_width=2)
        board.after_constructor()
        assert len(board.get_all_game_board_points_as_ordered_list()) == 4

    def test_points_creation_25(self) -> None:
        board = GameBoard(total_height=5, total_width=5)
        board.after_constructor()
        assert len(board.get_all_game_board_points_as_ordered_list()) == 25

    def test_point_creation(self) -> None:
        board = GameBoard(total_height=5, total_width=5)
        board.after_constructor()
        assert board.get_game_board_point(2, 2) is not None

    def test_neighbour(self) -> None:
        board = GameBoard(total_height=5, total_width=5)
        board.after_constructor()

        assert board.has_neighbour_game_board_point(
            board.get_game_board_point(2, 2),
            game.NeighbourGameBoardPointDirection.NORTH,
        )
