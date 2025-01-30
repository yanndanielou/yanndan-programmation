""" Example module that performs tetration """

from .exponentiation import exponentiation_custom


def tetration_custom(a: int, b: int) -> int:
    """Returns the product of two integers using addition."""
    if not b:
        return 1
    result = a
    for _ in range(abs(b) - 1):
        result = exponentiation_custom(result, a)
    return result
