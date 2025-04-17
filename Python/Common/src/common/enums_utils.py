from enum import Enum


class EnumWithRepr(Enum):
    def __repr__(self) -> str:
        return self.name
