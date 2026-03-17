# -*-coding:Utf-8 -*
"""test custom"""
import pytest

from src.common.custom_iterator import SimpleIntCustomIncrementDecrement, AlphabeticalLetterIncrementDecrement


class TestSimpleIntCustomIncrementDecrementTest:
    """SimpleIntCustomIncrementDecrementTest"""

    def test_increment(self) -> None:
        """test"""
        increment_test = SimpleIntCustomIncrementDecrement()
        assert 0 == increment_test.value
        assert 1 == increment_test.prefix_increment()
        assert 1 == increment_test.value
        assert 2 == increment_test.prefix_increment()
        assert 2 == increment_test.value
        assert 2 == increment_test.postfix_increment()
        assert 3 == increment_test.value

    def test_decrement(self) -> None:
        """test"""
        increment_test = SimpleIntCustomIncrementDecrement(10)
        assert 10 == increment_test.value
        assert 9 == increment_test.prefix_decrement()
        assert 9 == increment_test.value
        assert 8 == increment_test.prefix_decrement()
        assert 8 == increment_test.value
        assert 8 == increment_test.postfix_decrement()
        assert 7 == increment_test.value


class TestAlphabeticalLetterIncrementDecrement:
    def test_increment_default_value(self) -> None:
        """test"""
        increment_test = AlphabeticalLetterIncrementDecrement()
        assert "A" == increment_test.value

    def test_increment_capital(self) -> None:
        """test"""
        increment_test = AlphabeticalLetterIncrementDecrement("C")
        assert "C" == increment_test.value
        assert "D" == increment_test.prefix_increment()
        assert "D" == increment_test.value
        assert "E" == increment_test.prefix_increment()
        assert "E" == increment_test.value
        assert "E" == increment_test.postfix_increment()
        assert "F" == increment_test.value

    def test_increment_lower(self) -> None:
        """test"""
        increment_test = AlphabeticalLetterIncrementDecrement("c")
        assert "c" == increment_test.value
        assert "d" == increment_test.prefix_increment()
        assert "d" == increment_test.value
        assert "e" == increment_test.prefix_increment()
        assert "e" == increment_test.value
        assert "e" == increment_test.postfix_increment()
        assert "f" == increment_test.value

    def test_decrement_capital(self) -> None:
        """test"""
        decrement_test = AlphabeticalLetterIncrementDecrement("D")
        assert "D" == decrement_test.value
        assert "C" == decrement_test.prefix_decrement()
        assert "C" == decrement_test.value
        assert "B" == decrement_test.prefix_decrement()
        assert "B" == decrement_test.value
        assert "B" == decrement_test.postfix_decrement()
        assert "A" == decrement_test.value

    def test_decrement_lower(self) -> None:
        """test"""
        decrement_test = AlphabeticalLetterIncrementDecrement("d")
        assert "d" == decrement_test.value
        assert "c" == decrement_test.prefix_decrement()
        assert "c" == decrement_test.value
        assert "b" == decrement_test.prefix_decrement()
        assert "b" == decrement_test.value
        assert "b" == decrement_test.postfix_decrement()
        assert "a" == decrement_test.value
