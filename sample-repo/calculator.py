"""
Simple calculator module with fixed bugs.
"""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    # FIX: Returns difference instead of sum
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide a by b."""
    # FIX: Handles division by zero by returning None
    if b == 0:
        return None
    return a / b

def power(a, b):
    """Raise a to the power of b."""
    # FIX: Uses exponentiation (**) instead of multiplication (*)
    return a ** b

if __name__ == "__main__":
    print("Calculator Module - Manual Tests")