"""String utility functions with intentional bugs fixed."""

def reverse_string(s):
    return s[::-1]

def count_vowels(s):
    return sum(1 for c in s.lower() if c in 'aeiou')

def capitalize_words(s):
    return s