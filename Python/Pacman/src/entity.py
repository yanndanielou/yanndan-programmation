import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from random import randint
import nodes
from typing import List, cast
import constants
from abc import ABC, abstractmethod

from logger import logger_config


class Entity(object):

    def __init__(self, node: nodes.Node, name: int) -> None:
        self.name = name
        self.directions = {constants.UP: Vector2(0, -1), constants.DOWN: Vector2(0, 1), constants.LEFT: Vector2(-1, 0), constants.RIGHT: Vector2(1, 0), constants.STOP: Vector2()}
        self.direction = constants.STOP
        self.speed = self.setSpeed(constants.DEFAULT_ENTITY_SPEED)
        self.radius = 10
        self.collideRadius = 5
        self.color = constants.WHITE
        self.visible = True
        self.disablePortal = False
        self.goal: Vector2 = None
        self.directionMethod = self.randomDirection
        self.setStartNode(node)
        self.image = None

    def setPosition(self) -> None:
        self.position = self.node.position.copy()

    def update(self, dt: float) -> None:
        to_add = self.directions[self.direction] * self.speed * dt
        self.position += to_add

        if self.overshotTarget():
            self.node: nodes.Node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            if not self.disablePortal:
                if self.node.neighbors[PORTAL] is not None:
                    self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()

    def validDirection(self, direction: int) -> bool:
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False

    def getNewTarget(self, direction: int) -> nodes.Node:
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self) -> bool:
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target

        return False

    def reverseDirection(self) -> None:
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction: int) -> bool:
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def validDirections(self) -> List[int]:
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions: List[int]) -> int:
        return directions[randint(0, len(directions) - 1)]

    def goalDirection(self, directions: List[int]) -> int:
        distances = []
        for direction in directions:
            vec = self.node.position + self.directions[direction] * TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]

    def setStartNode(self, node: nodes.Node) -> None:
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    def setBetweenNodes(self, direction: int) -> None:
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    def reset(self) -> None:
        logger_config.print_and_log_info(f"Reset entity {self}")
        self.setStartNode(self.startNode)
        self.direction = constants.STOP
        self.speed = constants.DEFAULT_ENTITY_SPEED
        self.visible = True

    def setSpeed(self, speed: int) -> float:
        self.speed: float = speed * constants.TILEWIDTH / 16
        logger_config.print_and_log_info(f"Set speed {speed} to {self}, now, actual speed is {self.speed}")
        return self.speed

    def render(self, screen: pygame.surface.Surface) -> None:
        if self.visible:
            if self.image is not None:
                adjust = Vector2(constants.TILEWIDTH, constants.TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.asTuple())
            else:
                p = self.position.asInt()
                pygame.draw.circle(screen, self.color, p, self.radius)


class EntityGroup(ABC):
    @abstractmethod
    def __init__(self) -> None:
        self.all_entities: List[Entity] = []
