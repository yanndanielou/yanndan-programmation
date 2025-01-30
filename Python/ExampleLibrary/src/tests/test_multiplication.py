from examplelibrary.multiplication import multiply_custom


def test_multiply_custom() -> None:
    assert multiply_custom(2, 3) == 6
    assert multiply_custom(-1, 3) == -3
    assert not multiply_custom(0, 5)
    assert multiply_custom(4, -2) == -8
