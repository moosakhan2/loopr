"""
Simple calculator module with intentional bugs for testing the agent.

Bugs:
1. subtract() returns a+b instead of a-b
2. divide() doesn't handle division by zero
3. power() uses * instead of **
"""


def add(a, b):
    """Add two numbers."""
    return a + b


def subtract(a, b):
    """Subtract b from a."""
    # BUG: Returns sum instead of difference
    return a + b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def divide(a, b):
    """Divide a by b."""
    # BUG: Doesn't handle division by zero
    return a / b


def power(a, b):
    """Raise a to the power of b."""
    # BUG: Uses multiplication instead of exponentiation
    return a * b


if __name__ == "__main__":
    print("Calculator Module - Manual Tests")
    print("=" * 40)
    
    print(f"add(5, 3) = {add(5, 3)}")  # Expected: 8
    print(f"subtract(5, 3) = {subtract(5, 3)}")  # Expected: 2, Got: 8 (BUG)
    print(f"multiply(5, 3) = {multiply(5, 3)}")  # Expected: 15
    print(f"divide(6, 3) = {divide(6, 3)}")  # Expected: 2.0
    print(f"power(2, 3) = {power(2, 3)}")  # Expected: 8, Got: 6 (BUG)
    
    print("\nTesting edge cases:")
    try:
        print(f"divide(5, 0) = {divide(5, 0)}")  # Should handle gracefully (BUG)
    except ZeroDivisionError as e:
        print(f"divide(5, 0) raised ZeroDivisionError: {e}")

# Made with Bob
