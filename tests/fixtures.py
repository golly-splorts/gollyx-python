from golly_python.linkedlists import LifeList


def two_spinners_fixture():

    ROWS = 100
    COLS = 120
    binary = LifeList(ROWS, COLS)
    s1 = LifeList(ROWS, COLS)
    s2 = LifeList(ROWS, COLS)

    binary.insert(1, 1)
    binary.insert(1, 2)
    binary.insert(1, 3)
    binary.insert(10, 15)
    binary.insert(10, 16)
    binary.insert(10, 17)

    s1.insert(1, 1)
    s1.insert(10, 16)
    s1.insert(1, 3)

    s2.insert(10, 15)
    s2.insert(1, 2)
    s2.insert(10, 17)

    return binary, s1, s2


def multicolor_pi():

    ROWS = 100
    COLS = 120
    binary = LifeList(ROWS, COLS)
    s1 = LifeList(ROWS, COLS)
    s2 = LifeList(ROWS, COLS)

    binary.insert(1, 1)
    binary.insert(2, 1)
    binary.insert(3, 1)
    binary.insert(3, 2)

    s1.insert(1, 1)
    s1.insert(2, 1)
    s1.insert(3, 1)
    s1.insert(3, 2)

    binary.insert(1, 3)
    binary.insert(2, 3)
    binary.insert(3, 3)

    s2.insert(1, 3)
    s2.insert(2, 3)
    s2.insert(3, 3)

    return binary, s1, s2
