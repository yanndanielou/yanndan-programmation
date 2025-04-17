from enum import Enum, IntEnum


class NameBasedReprEnum(Enum):
    def __repr__(self) -> str:
        return self.name


class NameBasedReprIntEnum(IntEnum):
    def __repr__(self) -> str:
        return self.name
