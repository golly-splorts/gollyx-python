from golly_python.linkedlists import LifeList


def two_spinners_fixture():

    binary = LifeList()
    binary.insert(1, 1)
    binary.insert(1, 2)
    binary.insert(1, 3)
    binary.insert(10, 15)
    binary.insert(10, 16)
    binary.insert(10, 17)
    
    s1 = LifeList()
    s1.insert(1, 1)
    s1.insert(10, 16)
    s1.insert(1, 3)
    
    s2 = LifeList()
    s2.insert(10, 15)
    s2.insert(1, 2)
    s2.insert(10, 17)

    return binary, s1, s2
