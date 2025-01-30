from .addition import add_custom

def multiply_custom(a: int, b: int) -> int:
    """Returns the product of two integers using addition."""
    result = 0
    for _ in range(abs(b)):
        result = add_custom(result, a)
    return result if b >= 0 else -result
