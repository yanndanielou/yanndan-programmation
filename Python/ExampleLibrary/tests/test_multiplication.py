from ExampleLibrary.multiplication import multiply_custom

def test_multiply_custom():
    assert multiply_custom(2, 3) == 6
    assert multiply_custom(-1, 3) == -3
    assert multiply_custom(0, 5) == 0
    assert multiply_custom(4, -2) == -8
