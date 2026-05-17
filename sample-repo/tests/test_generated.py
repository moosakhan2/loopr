import sys
sys.path.insert(0, '.')
from calculator import *

def test_calculator_add():
    from calculator import add
    result = add(5, 3)
    assert result == 8

def test_calculator_subtract():
    from calculator import subtract
    result = subtract(5, 3)
    assert result == 2

def test_calculator_divide():
    from calculator import divide
    result = divide(10, 2)
    assert result == 5

def test_string_utils_capitalize_words():
    from string_utils import capitalize_words
    result = capitalize_words("hello world")
    assert result == "Hello World"