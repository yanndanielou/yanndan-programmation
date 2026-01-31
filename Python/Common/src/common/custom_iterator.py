# -*-coding:Utf-8 -*
"""Custom iterators"""

# from dataclasses import dataclass


# @dataclass
class SimpleIntCustomIncrementDecrement:
    """allows simple int counter"""

    def __init__(self, initial_value: int = 0):
        self._value: int = initial_value

    def prefix_increment(self, increment: int = 1) -> int:
        """equivalent to C++
        ++ unary-expression"""
        self._value += increment
        return self._value

    def postfix_increment(self, increment: int = 1) -> int:
        """equivalent to C++
        unary-expression ++"""
        previous_value = self._value
        self._value += increment
        return previous_value

    def prefix_decrement(self, decrement: int = 1) -> int:
        """equivalent to C++
        -- unary-expression"""
        return self.prefix_increment(-decrement)

    def postfix_decrement(self, decrement: int = 1) -> int:
        """equivalent to C++
        unary-expression --"""
        return self.postfix_increment(-decrement)

    @property
    def value(self) -> int:
        """Get current value"""
        return self._value


# @dataclass
class AlphabeticalLetterIncrementDecrement:

    def __init__(self, initial_letter: str = "A"):
        self.use_capital = initial_letter == initial_letter.upper()
        assert len(initial_letter) == 1
        self._int_value = ord(initial_letter)

    def prefix_increment(self, increment: int = 1) -> str:
        self._int_value += increment
        assert (self._int_value <= ord("Z") and self.use_capital) or self._int_value <= ord("z")
        return chr(self._int_value)

    def postfix_increment(self, increment: int = 1) -> str:
        previous_value = self._int_value
        self._int_value += increment
        return chr(previous_value)

    def prefix_decrement(self, decrement: int = 1) -> str:
        return self.prefix_increment(-decrement)

    def postfix_decrement(self, decrement: int = 1) -> str:
        return self.postfix_increment(-decrement)

    @property
    def value(self) -> str:
        """Get current value"""
        return chr(self._int_value)
