import pygame
from pygame.locals import K_RIGHT, K_LEFT, K_DOWN, K_UP  # pylint: disable=[no-name-in-module]
from pygame.locals import *
import pygame.locals
from vector import Vector2
from constants import *
import constants
from entity import Entity
from sprites import PacmanSprites
from typing import List, Optional, Any


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pellets
    import ghosts
    import nodes


class Pacman(Entity):
    def __init__(self, node: "nodes.Node") -> None:
        Entity.__init__(self, node=node, name=constants.PACMAN)

        self.color = constants.YELLOW
        self.direction = constants.LEFT
        self.setBetweenNodes(constants.LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)

    def reset(self) -> None:
        Entity.reset(self)
        self.direction = constants.LEFT
        self.setBetweenNodes(constants.LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self) -> None:
        self.alive = False
        self.direction = constants.STOP

    def update(self, dt: float) -> None:
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[constants.PORTAL] is not None:
                self.node = self.node.neighbors[constants.PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = constants.STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def getValidKey(self) -> int:
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return constants.UP
        if key_pressed[K_DOWN]:
            return constants.DOWN
        if key_pressed[K_LEFT]:
            return constants.LEFT
        if key_pressed[K_RIGHT]:
            return constants.RIGHT
        return constants.STOP

    def eatPellets(self, pelletList: List["pellets.Pellet"]) -> Optional["pellets.Pellet"]:
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost: "ghosts.Ghost") -> bool:
        return self.collideCheck(ghost)

    def collideCheck(self, other: Any) -> bool:
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius) ** 2
        if dSquared <= rSquared:
            return True
        return False
