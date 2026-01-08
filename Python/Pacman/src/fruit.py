import pygame
from entity import Entity
from constants import *
import constants
from sprites import FruitSprites

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import nodes


class Fruit(Entity):
    def __init__(self, node: "nodes.Node", level: int = 0) -> None:
        Entity.__init__(self, node)
        self.name = constants.FRUIT
        self.color = constants.GREEN
        self.lifespan = 5
        self.timer: float = 0
        self.destroy = False
        self.points = 100 + level * 20
        self.setBetweenNodes(constants.RIGHT)
        self.sprites = FruitSprites(self, level)

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True
