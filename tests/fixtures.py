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


def two_acorn_fixture():

    ROWS = 100
    COLS = 120
    binary = LifeList(ROWS, COLS)
    s1 = LifeList(ROWS, COLS)
    s2 = LifeList(ROWS, COLS)

    # acorn number 1
    binary.insert(50, 30)
    binary.insert(51, 30)
    binary.insert(54, 30)
    binary.insert(55, 30)
    binary.insert(56, 30)
    binary.insert(53, 31)
    binary.insert(51, 32)

    s1.insert(50, 30)
    s1.insert(51, 30)
    s1.insert(54, 30)
    s1.insert(55, 30)
    s1.insert(56, 30)
    s1.insert(53, 31)
    s1.insert(51, 32)


    # acorn number 2
    binary.insert(24, 92)
    binary.insert(25, 92)
    binary.insert(28, 92)
    binary.insert(29, 92)
    binary.insert(30, 92)
    binary.insert(27, 91)
    binary.insert(25, 90)

    s2.insert(24, 92)
    s2.insert(25, 92)
    s2.insert(28, 92)
    s2.insert(29, 92)
    s2.insert(30, 92)
    s2.insert(27, 91)
    s2.insert(25, 90)

    return binary, s1, s2

def multicolor_pi_fixture():

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
