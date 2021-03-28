from .constants import SMOL


def approx_equal(a, b, tol):
    return (abs(b - a) / abs(a + SMOL)) < tol
