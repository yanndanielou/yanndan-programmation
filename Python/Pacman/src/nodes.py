import pygame
from vector import Vector2
from constants import *
import numpy as np
import numpy
from typing import Tuple, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import entity


class Node(object):
    def __init__(self, x: int, y: int) -> None:
        self.position = Vector2(x, y)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL: None}
        self.access = {
            UP: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            DOWN: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            LEFT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            RIGHT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
        }

    def denyAccess(self, direction: int, entity: "entity.Entity") -> None:
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allowAccess(self, direction: int, entity: "entity.Entity") -> None:
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)

    def render(self, screen) -> None:
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.asInt(), 12)


class NodeGroup(object):
    def __init__(self, level: int) -> None:
        self.level = level
        self.nodesLUT = {}
        self.nodeSymbols = ["+", "P", "n"]
        self.pathSymbols = [".", "-", "|", "p"]
        data = self.readMazeFile(level)
        self.createNodeTable(data)
        self.connectHorizontally(data)
        self.connectVertically(data)
        self.homekey = None

    def readMazeFile(self, textfile: str) -> numpy.ndarray:
        return np.loadtxt(textfile, dtype="<U1")

    def createNodeTable(self, data, xoffset: int = 0, yoffset: int = 0) -> None:
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col + xoffset, row + yoffset)
                    self.nodesLUT[(x, y)] = Node(x, y)

    def constructKey(self, x: int, y: int) -> Tuple[int, int]:
        return x * TILEWIDTH, y * TILEHEIGHT

    def connectHorizontally(self, data, xoffset=0, yoffset=0) -> None:
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col + xoffset, row + yoffset)
                    else:
                        otherkey = self.constructKey(col + xoffset, row + yoffset)
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None

    def connectVertically(self, data, xoffset=0, yoffset=0) -> None:
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col + xoffset, row + yoffset)
                    else:
                        otherkey = self.constructKey(col + xoffset, row + yoffset)
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]
                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

    def getStartTempNode(self) -> None:
        nodes = list(self.nodesLUT.values())
        return nodes[0]

    def setPortalPair(self, pair1: Tuple[int, int], pair2: Tuple[int, int]) -> None:
        key1 = self.constructKey(*pair1)
        key2 = self.constructKey(*pair2)
        if key1 in self.nodesLUT.keys() and key2 in self.nodesLUT.keys():
            self.nodesLUT[key1].neighbors[PORTAL] = self.nodesLUT[key2]
            self.nodesLUT[key2].neighbors[PORTAL] = self.nodesLUT[key1]

    def createHomeNodes(self, xoffset: float, yoffset: float) -> None:
        homedata = np.array([["X", "X", "+", "X", "X"], ["X", "X", ".", "X", "X"], ["+", "X", ".", "X", "+"], ["+", ".", "+", ".", "+"], ["+", "X", "X", "X", "+"]])

        self.createNodeTable(homedata, xoffset, yoffset)
        self.connectHorizontally(homedata, xoffset, yoffset)
        self.connectVertically(homedata, xoffset, yoffset)
        self.homekey = self.constructKey(xoffset + 2, yoffset)
        return self.homekey

    def connectHomeNodes(self, homekey: Tuple[int, int], otherkey: Tuple[int, int], direction: int) -> None:
        key = self.constructKey(*otherkey)
        self.nodesLUT[homekey].neighbors[direction] = self.nodesLUT[key]
        self.nodesLUT[key].neighbors[direction * -1] = self.nodesLUT[homekey]

    def getNodeFromPixels(self, xpixel, ypixel) -> None:
        if (xpixel, ypixel) in self.nodesLUT.keys():
            return self.nodesLUT[(xpixel, ypixel)]
        return None

    def getNodeFromTiles(self, col: int, row: int) -> Optional[Node]:
        x, y = self.constructKey(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None

    def denyAccess(self, col: float, row: float, direction: int, entity: "entity.Entity") -> None:
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.denyAccess(direction, entity)

    def allowAccess(self, col: float, row: float, direction: int, entity: "entity.Entity") -> None:
        node = self.getNodeFromTiles(col, row)
        if node is not None:
            node.allowAccess(direction, entity)

    def denyAccessList(self, col: float, row: float, direction: int, entities) -> None:
        for entity in entities:
            self.denyAccess(col, row, direction, entity)

    def allowAccessList(self, col: float, row: float, direction: int, entities) -> None:
        for entity in entities:
            self.allowAccess(col, row, direction, entity)

    def denyHomeAccess(self, entity: "entity.Entity") -> None:
        self.nodesLUT[self.homekey].denyAccess(DOWN, entity)

    def allowHomeAccess(self, entity: "entity.Entity") -> None:
        self.nodesLUT[self.homekey].allowAccess(DOWN, entity)

    def denyHomeAccessList(self, entities) -> None:
        for entity in entities:
            self.denyHomeAccess(entity)

    def allowHomeAccessList(self, entities) -> None:
        for entity in entities:
            self.allowHomeAccess(entity)

    def render(self, screen) -> None:
        for node in self.nodesLUT.values():
            node.render(screen)
