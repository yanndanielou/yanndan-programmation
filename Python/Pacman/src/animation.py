from constants import *
import constants
from typing import List, Tuple


class Animator(object):
    def __init__(self, frames: Tuple[Tuple[int, int], ...], speed: int = 20, loop: bool = True) -> None:
        self.frames = frames
        self.current_frame: int = 0
        self.speed = speed
        self.loop = loop
        self.dt: float = 0
        self.finished: bool = False

    def reset(self) -> None:
        self.current_frame = 0
        self.finished = False

    def update(self, dt: float) -> Tuple[int, int]:
        if not self.finished:
            self.nextFrame(dt)
        if self.current_frame == len(self.frames):
            if self.loop:
                self.current_frame = 0
            else:
                self.finished = True
                self.current_frame -= 1

        return self.frames[self.current_frame]

    def nextFrame(self, dt: float) -> None:
        self.dt += dt
        if self.dt >= (1.0 / self.speed):
            self.current_frame += 1
            self.dt = 0
