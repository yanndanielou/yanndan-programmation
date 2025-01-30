from ExampleLibrary.addition import add_custom

def test_add_custom():
    assert add_custom(2, 3) == 5
    assert add_custom(-1, 1) == 0
    assert add_custom(0, 0) == 0
