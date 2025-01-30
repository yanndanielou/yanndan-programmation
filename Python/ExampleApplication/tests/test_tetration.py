from exampleapplication.tetration import tetration_custom


def test_tetration_custom_2_0() -> None:
    assert tetration_custom(2, 0) == 1


def test_tetration_custom_2_1() -> None:
    assert tetration_custom(2, 1) == 2


def test_tetration_custom_2_2() -> None:
    assert tetration_custom(2, 2) == 4


def test_tetration_custom_2_3() -> None:
    assert tetration_custom(2, 3) == 16
