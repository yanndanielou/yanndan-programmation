# -*-coding:Utf-8 -*
""" test custom """
import pytest

from  src.common.custom_iterator import SimpleIntCustomIncrementDecrement

class TestSimpleIntCustomIncrementDecrementTest():
    """ SimpleIntCustomIncrementDecrementTest """

    def test_increment(self) -> None:
        """ test """
        increment_test:SimpleIntCustomIncrementDecrement = SimpleIntCustomIncrementDecrement()
        assert 0 == increment_test.value
        assert 1 == increment_test.prefix_increment()
        assert 1 == increment_test.value
        assert 2 == increment_test.prefix_increment()
        assert 2 == increment_test.value
        assert 2 == increment_test.postfix_increment()
        assert 3 == increment_test.value

    def test_decrement(self) -> None:
        """ test """
        increment_test:SimpleIntCustomIncrementDecrement = SimpleIntCustomIncrementDecrement(10)
        assert 10 == increment_test.value
        assert 9 == increment_test.prefix_decrement()
        assert 9 == increment_test.value
        assert 8 == increment_test.prefix_decrement()
        assert 8 == increment_test.value
        assert 8 == increment_test.postfix_decrement()
        assert 7 == increment_test.value
