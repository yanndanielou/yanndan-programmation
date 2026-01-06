import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
import constants
from entity import Entity
from modes import ModeController
from sprites import GhostSprites
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import nodes
    import pacman
    import ghosts


class Ghost(Entity):
    def __init__(self, node: "nodes.Node", pacman: Optional["pacman.Pacman"] = None, blinky: Optional["ghosts.Blinky"] = None):
        Entity.__init__(self, node)
        self.name = constants.GHOST
        self.points = 200
        self.goal = Vector2()
        self.directionMethod = self.goalDirection
        self.pacman = pacman
        self.mode = ModeController(self)
        self.blinky = blinky
        self.homeNode = node

    def reset(self) -> None:
        Entity.reset(self)
        self.points = 200
        self.directionMethod = self.goalDirection

    def update(self, dt: float) -> None:
        self.sprites.update(dt)
        self.mode.update(dt)
        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()
        Entity.update(self, dt)

    def scatter(self) -> None:
        self.goal = Vector2()

    def chase(self) -> None:
        self.goal = self.pacman.position

    def spawn(self) -> None:
        self.goal = self.spawnNode.position

    def setSpawnNode(self, node: "nodes.Node") -> None:
        self.spawnNode = node

    def startSpawn(self) -> None:
        self.mode.setSpawnMode()
        if self.mode.current == SPAWN:
            self.setSpeed(constants.GHOST_SPAWN_SPEED)
            self.directionMethod = self.goalDirection
            self.spawn()

    def startFreight(self) -> None:
        self.mode.setFreightMode()
        if self.mode.current == FREIGHT:
            self.setSpeed(constants.GHOST_FREIGHT_SPEED)
            self.directionMethod = self.randomDirection

    def normalMode(self) -> None:
        self.setSpeed(constants.GHOST_NORMAL_SPEED)
        self.directionMethod = self.goalDirection
        self.homeNode.denyAccess(DOWN, self)


class Blinky(Ghost):
    def __init__(self, node: "nodes.Node", pacman: Optional["pacman.Pacman"] = None, blinky: Optional["ghosts.Blinky"] = None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = BLINKY
        self.color = RED
        self.sprites = GhostSprites(self)


class Pinky(Ghost):
    def __init__(self, node: "nodes.Node", pacman: Optional["pacman.Pacman"] = None, blinky: Optional[Blinky] = None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = PINKY
        self.color = PINK
        self.sprites = GhostSprites(self)

    def scatter(self) -> None:
        self.goal = Vector2(TILEWIDTH * NCOLS, 0)

    def chase(self) -> None:
        assert self.pacman, "YDA FIXME"
        self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4


class Inky(Ghost):
    def __init__(self, node: "nodes.Node", pacman: Optional["pacman.Pacman"] = None, blinky: Optional[Blinky] = None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = INKY
        self.color = TEAL
        self.sprites = GhostSprites(self)

    def scatter(self) -> None:
        self.goal = Vector2(TILEWIDTH * NCOLS, TILEHEIGHT * NROWS)

    def chase(self) -> None:
        vec1 = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 2
        vec2 = (vec1 - self.blinky.position) * 2
        self.goal = self.blinky.position + vec2


class Clyde(Ghost):
    def __init__(self, node: "nodes.Node", pacman: Optional["pacman.Pacman"] = None, blinky: Optional[Blinky] = None) -> None:
        Ghost.__init__(self, node, pacman, blinky)
        self.name = CLYDE
        self.color = ORANGE
        self.sprites = GhostSprites(self)

    def scatter(self) -> None:
        self.goal = Vector2(0, TILEHEIGHT * NROWS)

    def chase(self) -> None:
        d = self.pacman.position - self.position
        ds = d.magnitudeSquared()
        if ds <= (TILEWIDTH * 8) ** 2:
            self.scatter()
        else:
            self.goal = self.pacman.position + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4


class GhostGroup(object):
    def __init__(self, node: "nodes.Node", pacman: "pacman.Pacman") -> None:
        self.blinky = Blinky(node, pacman)
        self.pinky = Pinky(node, pacman)
        self.inky = Inky(node, pacman, self.blinky)
        self.clyde = Clyde(node, pacman)
        self.ghosts: List[Ghost] = [self.blinky, self.pinky, self.inky, self.clyde]

    def __iter__(self) -> List[Ghost]:
        # assert False, "Use ghosts instead"
        return iter(self.ghosts)

    def update(self, dt: float) -> None:
        for ghost in self:
            ghost.update(dt)

    def startFreight(self) -> None:
        for ghost in self:
            ghost.startFreight()
        self.resetPoints()

    def setSpawnNode(self, node):
        for ghost in self.ghosts:
            ghost.setSpawnNode(node)

    def updatePoints(self) -> None:
        for ghost in self:
            ghost.points *= 2

    def resetPoints(self) -> None:
        for ghost in self:
            ghost.points = 200

    def hide(self) -> None:
        for ghost in self:
            ghost.visible = False

    def show(self) -> None:
        for ghost in self:
            ghost.visible = True

    def reset(self) -> None:
        for ghost in self:
            ghost.reset()

    def render(self, screen: pygame.surface.Surface) -> None:
        for ghost in self:
            ghost.render(screen)
