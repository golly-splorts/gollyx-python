from .constants import SMOL


def lists_equal(a, b):
    if len(a) != len(b):
        return False
    for ia, ib in zip(a, b):
        if ia != ib:
            return False
    return True

def approx_equal(a, b, tol):
    return (abs(b - a) / abs(a + SMOL)) < tol
