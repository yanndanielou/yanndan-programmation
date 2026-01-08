from typing import Optional, Callable


class Pause(object):
    def __init__(self, paused: bool = False) -> None:
        self.paused = paused
        self.timer: float = 0
        self.pauseTime: Optional[int] = None
        self.func: Optional[Callable] = None

    def update(self, dt: float) -> Optional[Callable]:
        if self.pauseTime is not None:
            self.timer += dt
            if self.timer >= self.pauseTime:
                self.timer = 0
                self.paused = False
                self.pauseTime = None
                return self.func
        return None

    def setPause(self, playerPaused: bool = False, pauseTime: Optional[int] = None, func: Optional[Callable] = None) -> None:
        self.timer = 0
        self.func = func
        self.pauseTime = pauseTime
        self.flip()

    def flip(self) -> None:
        self.paused = not self.paused
