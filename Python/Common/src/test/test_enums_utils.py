import pytest

from src.common import enums_utils

from enum import auto


class NameBasedEnumExample(enums_utils.NameBasedEnum):
    A = auto()
    B = auto()


class NameBasedIntEnumExample(enums_utils.NameBasedIntEnum):
    ONE = auto()
    TWO = auto()


class TestNameBasedReprEnum:
    def test_repr(self) -> None:
        assert f"{NameBasedEnumExample.A}" == "A"
        assert str(NameBasedEnumExample.A) == "A"


class TestNameBasedReprIntEnum:
    def test_repr(self) -> None:
        assert f"{NameBasedIntEnumExample.ONE}" == "ONE"
        assert str(NameBasedIntEnumExample.ONE) == "ONE"
