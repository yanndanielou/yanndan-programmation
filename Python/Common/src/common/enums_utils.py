from enum import Enum, IntEnum


class NameBasedEnum(Enum):
    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class NameBasedIntEnum(IntEnum):
    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name
