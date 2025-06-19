from exampleapplication.exponentiation import exponentiation_custom


def test_exponentiation_custom_0() -> None:
    assert exponentiation_custom(2, 0) == 1


def test_exponentiation_custom_1() -> None:
    assert exponentiation_custom(2, 1) == 2


def test_exponentiation_custom_3() -> None:
    assert exponentiation_custom(2, 3) == 8


def test_exponentiation_custom_4() -> None:
    assert exponentiation_custom(2, 4) == 16
