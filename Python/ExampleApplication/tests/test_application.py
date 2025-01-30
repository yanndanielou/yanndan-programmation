from exampleapplication.main import add_custom


def test_add_custom() -> None:
    assert add_custom(2, 3) == 5
    assert not add_custom(-1, 1)
    assert not add_custom(0, 0)
