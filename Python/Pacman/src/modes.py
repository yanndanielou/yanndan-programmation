from constants import *
import constants

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import entity
    import ghosts


class MainMode(object):
    def __init__(self) -> None:
        self.timer: float = 0

        # those are initialized latter in scatter
        self.mode: int = -1
        self.time: int = -1
        self.timer: int = -1

        self.scatter()

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.time:
            if self.mode is constants.SCATTER:
                self.chase()
            elif self.mode is constants.CHASE:
                self.scatter()

    def scatter(self) -> None:
        self.mode = constants.SCATTER
        self.time = 7
        self.timer = 0

    def chase(self) -> None:
        self.mode = constants.CHASE
        self.time = 20
        self.timer = 0


class ModeController(object):
    def __init__(self, entity: "ghosts.Ghost") -> None:
        self.timer: float = 0
        self.time: Optional[float] = None
        self.mainmode = MainMode()
        self.current = self.mainmode.mode
        self.entity = entity

    def update(self, dt: float) -> None:
        self.mainmode.update(dt)
        if self.current is constants.FREIGHT:
            self.timer += dt
            assert self.time
            if self.timer >= self.time:
                self.time = None
                self.entity.normalMode()
                self.current = self.mainmode.mode
        elif self.current in [constants.SCATTER, constants.CHASE]:
            self.current = self.mainmode.mode

        if self.current is constants.SPAWN:
            if self.entity.node == self.entity.spawnNode:
                self.entity.normalMode()
                self.current = self.mainmode.mode

    def setFreightMode(self) -> None:
        if self.current in [constants.SCATTER, constants.CHASE]:
            self.timer = 0
            self.time = 7
            self.current = constants.FREIGHT
        elif self.current is constants.FREIGHT:
            self.timer = 0

    def setSpawnMode(self) -> None:
        if self.current is constants.FREIGHT:
            self.current = constants.SPAWN
