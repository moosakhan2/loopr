import sys
sys.path.insert(0, '.')
from string_utils import *
from calculator import *

def test_add_positive():
    assert add(2, 3) == 5

def test_subtract_returns_difference():
    assert subtract(5, 3) == 2

def test_reverse_string_empty():
    assert reverse_string("") == ""

def test_count_vowels_no_vowels():
    assert count_vowels("bcdf") == 0

def test_multiply_returns_product():
    assert multiply(4, 5) == 20

def test_power_returns_squared():
    assert power(4, 2) == 16