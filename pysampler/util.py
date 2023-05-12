import math

def db_to_linear(n):
    """Converts decibel value to linear"""
    return 10 ** (n/20)

def linear_to_db(n):
    """Converts linear value to decibel"""
    return math.log10(abs(n)) * 20