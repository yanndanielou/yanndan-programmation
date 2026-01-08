from constants import *
import constants

from typing import Dict, Tuple, TYPE_CHECKING, Callable

if TYPE_CHECKING:
    import nodes
    import ghosts


class MazeBase(object):
    def __init__(
        self,
        name: str,
        ghost_node_deny: Dict[int, Tuple[Tuple[int, ...]]],
        portalPairs: Dict[int, Tuple[Tuple[int, int]]],
        homeoffset: Tuple[float, int],
        homenodeconnectLeft: Tuple[int, int],
        homenodeconnectRight: Tuple[int, int],
        fruitStart: Tuple[int, int],
        pacmanStart: Tuple[int, int],
    ) -> None:
        self.portalPairs = portalPairs
        self.homeoffset = homeoffset
        self.ghostNodeDeny = ghost_node_deny
        self.name = name
        self.homenodeconnectLeft = homenodeconnectLeft
        self.homenodeconnectRight = homenodeconnectRight
        self.fruitStart = fruitStart
        self.pacmanStart = pacmanStart

    def setPortalPairs(self, nodes: "nodes.NodeGroup") -> None:
        for pair in list(self.portalPairs.values()):
            nodes.setPortalPair(*pair)

    def connectHomeNodes(self, nodes: "nodes.NodeGroup") -> None:
        key = nodes.createHomeNodes(*self.homeoffset)
        nodes.connectHomeNodes(key, self.homenodeconnectLeft, LEFT)
        nodes.connectHomeNodes(key, self.homenodeconnectRight, RIGHT)

    def addOffset(self, x: int, y: int) -> Tuple[float,]:
        return x + self.homeoffset[0], y + self.homeoffset[1]

    def denyGhostsAccess(self, ghosts: "ghosts.GhostGroup", nodes: "nodes.NodeGroup") -> None:
        nodes.denyAccessList(*(self.addOffset(2, 3) + (LEFT, ghosts)))
        nodes.denyAccessList(*(self.addOffset(2, 3) + (RIGHT, ghosts)))

        for direction in list(self.ghostNodeDeny.keys()):
            for values in self.ghostNodeDeny[direction]:
                nodes.denyAccessList(*(values + (direction, ghosts)))


class Maze1(MazeBase):
    def __init__(self) -> None:
        MazeBase.__init__(
            self,
            name="maze1",
            ghost_node_deny={constants.UP: ((12, 14), (15, 14), (12, 26), (15, 26)), constants.LEFT: (self.addOffset(2, 3),), constants.RIGHT: (self.addOffset(2, 3),)},
            homenodeconnectLeft=(12, 14),
            homenodeconnectRight=(15, 14),
            pacmanStart=(15, 26),
            homeoffset=(11.5, 14),
            portalPairs={0: ((0, 17), (27, 17))},
            fruitStart=(9, 20),
        )


class Maze2(MazeBase):
    def __init__(self) -> None:
        MazeBase.__init__(
            self,
            name="maze2",
            portalPairs={0: ((0, 4), (27, 4)), 1: ((0, 26), (27, 26))},
            homeoffset=(11.5, 14),
            homenodeconnectLeft=(9, 14),
            homenodeconnectRight=(18, 14),
            pacmanStart=(16, 26),
            fruitStart=(11, 20),
            ghost_node_deny={constants.UP: ((9, 14), (18, 14), (11, 23), (16, 23)), constants.LEFT: (self.addOffset(2, 3),), constants.RIGHT: (self.addOffset(2, 3),)},
        )


class MazeData(object):
    def __init__(self) -> None:
        self.obj = None
        self.mazedict: Dict[int, Callable] = {0: Maze1, 1: Maze2}

    def loadMaze(self, level: int) -> None:
        self.obj = self.mazedict[level % len(self.mazedict)]()
