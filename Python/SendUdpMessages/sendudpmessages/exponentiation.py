""" Example module that performs multiplication """

from examplelibrary import multiplication


def exponentiation_custom(a: int, b: int) -> int:
    """Returns the product of two integers using addition."""
    if not b:
        return 1
    result = a
    for _ in range(abs(b) - 1):
        result = multiplication.multiply_custom(result, a)
    return result


def not_typed_return(a: int, b: int):
    return a + b
