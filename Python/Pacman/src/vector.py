import math
from typing import Tuple, Optional, cast
from warnings import deprecated


class Vector2:
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y
        self.thresh = 0.000001

    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(self.x - other.x, self.y - other.y)

    def __neg__(self) -> "Vector2":
        return Vector2(-self.x, -self.y)

    def __mul__(self, scalar: int) -> "Vector2":
        return Vector2(self.x * scalar, self.y * scalar)

    def __div__(self, scalar: int) -> Optional["Vector2"]:
        if scalar != 0:
            return Vector2(self.x / float(scalar), self.y / float(scalar))
        return None

    def __truediv__(self, scalar: int) -> Optional["Vector2"]:
        return self.__div__(scalar)

    def __eq__(self, other: object) -> bool:
        other = cast(Vector2, other)
        if abs(self.x - other.x) < self.thresh:
            if abs(self.y - other.y) < self.thresh:
                return True
        return False

    def magnitudeSquared(self) -> float:
        return self.x**2 + self.y**2

    def magnitude(self) -> float:
        return math.sqrt(self.magnitudeSquared())

    def copy(self) -> "Vector2":
        return Vector2(self.x, self.y)

    def asTuple(self) -> Tuple[float, float]:
        return self.x, self.y

    @deprecated("Returns tuple by mistake?")
    def asInt(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    def __str__(self) -> str:
        return "<" + str(self.x) + ", " + str(self.y) + ">"
