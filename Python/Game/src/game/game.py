from typing import List, Dict
from enum import Enum
from collections import defaultdict


class NeighbourGameBoardPointDirection(Enum):
    """
    Enumeration for neighbor directions.
    """

    NORTH = "NORTH"
    NORTH_EAST = "NORTH_EAST"
    EAST = "EAST"
    SOUTH_EAST = "SOUTH_EAST"
    SOUTH = "SOUTH"
    SOUTH_WEST = "SOUTH_WEST"
    WEST = "WEST"
    NORTH_WEST = "NORTH_WEST"


class GenericIntegerGameBoardPoint:
    """
    Represents a point on the game board with integer coordinates.
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.neighbours: Dict[
            NeighbourGameBoardPointDirection, GenericIntegerGameBoardPoint
        ] = {}

    def set_neighbour(
        self,
        direction: NeighbourGameBoardPointDirection,
        neighbour: "GenericIntegerGameBoardPoint",
    ) -> None:
        self.neighbours[direction] = neighbour

    def get_neighbours(
        self,
    ) -> Dict[NeighbourGameBoardPointDirection, "GenericIntegerGameBoardPoint"]:
        return self.neighbours.values()

    def get_short_description(self) -> str:
        return f"GameBoardPoint :[{self.x},{self.y}]"


class GenericGameBoard:
    """
    Abstract class for a generic game board.
    """

    def __init__(self, total_width: int, total_height: int) -> None:
        self._total_width = total_width
        self._total_height = total_height
        self.game_board_points_by_x_and_y: list[
            list[GenericIntegerGameBoardPoint | None]
        ] = []
        self.game_board_points_per_y: Dict[int, List[GenericIntegerGameBoardPoint]] = (
            defaultdict(list)
        )
        self.all_game_board_points: list[GenericIntegerGameBoardPoint] = []
        # self.after_constructor()

    def after_constructor(self) -> None:
        self.create_initial_game_board_points()
        self.compute_neighbours_of_each_game_board_point()

    def create_initial_game_board_points(self) -> None:

        self.game_board_points_by_x_and_y = [
            [None for _ in range(self.get_total_width())]
            for _ in range(self.get_total_height())
        ]
        for x in range(self.get_total_width()):
            for y in range(self.get_total_height()):
                point = self.create_game_board_point(x, y)
                self.game_board_points_by_x_and_y[x][y] = point
                self.all_game_board_points.append(point)
                self.game_board_points_per_y[y].append(point)

    def compute_neighbours_of_each_game_board_point(self) -> None:
        for point in self.all_game_board_points:
            for direction in NeighbourGameBoardPointDirection:
                neighbour = self.get_neighbour_game_board_point(point, direction)
                if neighbour:
                    point.set_neighbour(direction, neighbour)

    def get_neighbour_game_board_point(
        self,
        reference_point: GenericIntegerGameBoardPoint,
        direction: NeighbourGameBoardPointDirection,
    ) -> GenericIntegerGameBoardPoint | None:
        x, y = reference_point.x, reference_point.y
        direction_map = {
            NeighbourGameBoardPointDirection.NORTH: (x, y - 1),
            NeighbourGameBoardPointDirection.NORTH_EAST: (x + 1, y - 1),
            NeighbourGameBoardPointDirection.EAST: (x + 1, y),
            NeighbourGameBoardPointDirection.SOUTH_EAST: (x + 1, y + 1),
            NeighbourGameBoardPointDirection.SOUTH: (x, y + 1),
            NeighbourGameBoardPointDirection.SOUTH_WEST: (x - 1, y + 1),
            NeighbourGameBoardPointDirection.WEST: (x - 1, y),
            NeighbourGameBoardPointDirection.NORTH_WEST: (x - 1, y - 1),
        }
        new_x, new_y = direction_map[direction]
        try:
            return self.game_board_points_by_x_and_y[new_x][new_y]
        except IndexError as _:
            return None

    def get_all_game_board_points_as_ordered_list(
        self,
    ) -> List[GenericIntegerGameBoardPoint]:
        return self.all_game_board_points

    def get_game_board_point(self, x: int, y: int) -> GenericIntegerGameBoardPoint:
        return self.game_board_points_by_x_and_y[x][y]

    def get_game_board_points_by_y(self, y: int) -> List[GenericIntegerGameBoardPoint]:
        return self.game_board_points_per_y.get(y, [])

    def has_neighbour_game_board_point(
        self,
        point: GenericIntegerGameBoardPoint,
        direction: NeighbourGameBoardPointDirection,
    ) -> bool:
        return self.get_neighbour_game_board_point(point, direction) is not None

    def create_game_board_point(self, x: int, y: int) -> GenericIntegerGameBoardPoint:
        raise NotImplementedError("Subclasses must implement create_game_board_point.")

    def get_total_width(self) -> int:
        return self._total_width

    def get_total_height(self) -> int:
        return self._total_height
