from linkedlists import (
    ListBase,
    SortedRowList,
    LifeList,
)


def test_row_list():
    lb = ListBase()
    print(lb.length())

    srl = SortedRowList(151, 10)
    print(srl)
    srl.insert(155)
    print(srl)
    srl.insert(154)
    print(srl)
    srl.insert(152)
    print(srl)
    srl.insert(-17)
    print(srl)
    srl.insert(-20)
    print(srl)
    srl.insert(-4)
    print(srl)
    srl.insert(152)
    print(srl)
    srl.insert(153)
    print(srl)
    srl.insert(152)
    print(srl)
    print(srl.head())


def test_life_list():

    ll = LifeList()
    ll.insert(151, 10)
    ll.insert(155, 10)
    ll.insert(154, 10)
    ll.insert(1, 42)
    ll.insert(2, 42)
    ll.insert(152, 10)
    ll.insert(153, 10)
    ll.insert(150, 11)
    ll.insert(152, 11)
    ll.insert(156, 12)
    ll.insert(149, 12)
    ll.insert(155, 12)
    print(ll)
    print(ll.live_count())
    ll.insert(1, 42)
    ll.insert(2, 42)
    print(ll.live_count())

    print("contains 155, 12 (should be true):")
    print(ll.contains(155, 12))
    print("contains 12, 155 (should be false):")
    print(ll.contains(12, 155))
    print("contains 151, 10 (should be true):")
    print(ll.contains(151, 10))
    print("contains 150, 10 (should be false):")
    print(ll.contains(150, 10))
    print(f"cell count: {ll.live_count()}")

    # Remove a cell in the list
    print(" -----8<------ removing cell")
    result = ll.remove(155, 12)
    print(f"Result of remove(155,12) operation: {result}")
    print(ll)
    print(f"contains 155, 12 (should be false): {ll.contains(155,12)}")
    print(f"cell count: {ll.live_count()}")

    # Remove a cell not in the list
    print(" -----8<------ removing cell")
    result = ll.remove(150, 10)
    print(f"Result of remove(150,10) operation (should be false): {result}")
    print(ll)
    print(f"contains 150, 10 (should be false): {ll.contains(150,10)}")
    print(f"cell count: {ll.live_count()}")


def test_insert_many():

    srl = SortedRowList(10)
    srl.insert(155)
    srl.insert(154)
    srl.insert(152)
    srl.insert(-17)
    srl.insert(-20)
    srl.insert(-4)
    print(srl)

    srl.insert_many_sorted([88, 152, 181])
    print(srl)
    srl.insert_many_sorted([152, 153, 154])
    print(srl)


def test_copy_life_list():

    import random

    print("Life List 1a:")
    l1a = LifeList()
    for i in range(10):
        l1a.insert(90, 100 + i)
        l1a.insert(91, 100 + i)
        l1a.insert(92, 100 + i)
        l1a.insert(93, 100 + i)
    print(l1a)
    print("live count (should be 40):")
    print(l1a.live_count())

    print("Life List 1b:")
    l1b = LifeList()
    for i in range(10):
        l1b.insert(90, 180 + i)
        l1b.insert(91, 180 + i)
        l1b.insert(92, 180 + i)
        l1b.insert(93, 180 + i)
    print(l1b)
    print("live count (should be 40):")
    print(l1b.live_count())

    print("Life List 1c:")
    l1c = LifeList()
    for i in range(10):
        l1c.insert(88 + i, 170)
    print(l1c)
    print("live count (should be 10):")
    print(l1c.live_count())

    l2 = LifeList()
    l2.insert(90, 170)
    l2.insert(91, 171)

    print("Life List 2 before copy:")
    print(l2)
    print("live count (should be 2):")
    print(l2.live_count())

    l2.copy_points(l1a)
    l2.copy_points(l1b)
    l2.copy_points(l1c)

    print("Life List 2 after copy:")
    print(l2)
    print("live count (should be 91):")
    print(l2.live_count())


def test_get_neighbor_count():

    i = LifeList()
    i.insert(50, 10)
    i.insert(49, 11)
    i.insert(50, 11)
    i.insert(51, 11)
    print(i)
    print(i.live_count())
    print("Neighbor count for 50, 10 (should be 3):")
    print(i.get_neighbor_count(50, 10))

    print("\n\n")

    i.insert(49, 10)
    i.insert(50, 9)
    print(i)
    print(f"Live count: {i.live_count()}")
    print("Neighbor count for 50, 10 (should be 5):")
    print(i.get_neighbor_count(50, 10))

    print("\n\n")

    i.remove(50, 11)
    i.remove(51, 11)
    i.remove(49, 10)
    print(i)
    print(f"Live count: {i.live_count()}")
    print("Neighbor count for 50, 10 (should be 2):")
    print(i.get_neighbor_count(50, 10))

    print("\n\n")

    i.insert(100, 100)
    i.insert(102, 100)
    i.insert(101, 101)
    i.insert(101, 102)
    print(i)
    print(f"Live count: {i.live_count()}")
    print("Neighbor count for 101, 101 (should be 3):")
    print(i.get_neighbor_count(101, 101))


def test_get_dead_neighbor_counts():

    # i = LifeList()
    # i.insert(1, 1)
    # print("State:")
    # print(i)
    # print("Dead neighbor counts:")
    # print(i.get_dead_neighbor_counts())

    # print("")

    # Vertical line
    # dead neighbr count should be 3 for two cells:
    # (0, 2)
    # (2, 2)
    j = LifeList()
    j.insert(1, 1)
    j.insert(1, 2)
    j.insert(1, 3)
    print("State:")
    print(j)
    print("Dead neighbor counts:")
    print(j.get_dead_neighbor_counts())
    print("Should contain the entry 2: [0: 3, 2: 3]")


def test_get_all_neighbor_counts():

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

    print("Binary state:")
    print(binary)
    print("State 1:")
    print(s1)
    print("State 2:")
    print(s2)

    (
        dead_neighbors,
        color1_dead_neighbors,
        color2_dead_neighbors,
        alive_neighbors,
        color1_neighbors,
        color2_neighbors,
    ) = binary.get_all_neighbor_counts(s1, s2)

    print("Dead neighbor counts:")
    print(dead_neighbors)
    print("Should contain the entry 2: [0: 3, 2: 3]")
    print("Should contain the entry 16: [9: 3, 11: 3]")
    print("Color 1 dead neighbor counts:")
    print(color1_dead_neighbors)
    print("Color 2 dead neighbor counts:")
    print(color2_dead_neighbors)

    print("")

    print("Alive neighbor counter:")
    print(alive_neighbors)
    print("Color 1 neighbor counter:")
    print(color1_neighbors)
    print("Color 2 neighbor counter:")
    print(color2_neighbors)


def test_dead_neighbors_filter():

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

    (
        dead_neighbors,
        color1_dead_neighbors,
        color2_dead_neighbors,
        alive_neighbors,
        color1_neighbors,
        color2_neighbors,
    ) = binary.get_all_neighbor_counts(s1, s2)

    dead_neighbors.filter(3, 3)
    print(dead_neighbors)


def test_dead_alive():

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

    print("Before:")
    print(binary)
    print("Before s1:")
    print(s1)
    print("Before s2:")
    print(s2)

    # print("="*40)

    # print("Before get all neighbor counts:")
    # print(binary)
    # print("before get all neighbor counts s1:")
    # print(s1)
    # print("before get all neighbor counts s2:")
    # print(s2)

    (
        dead_neighbors,
        color1_dead_neighbors,
        color2_dead_neighbors,
        alive_neighbors,
        color1_neighbors,
        color2_neighbors,
    ) = binary.get_all_neighbor_counts(s1, s2)

    # print("After get all neighbor counts:")
    # print(binary)
    # print("after get all neighbor counts s1:")
    # print(s1)
    # print("after get all neighbor counts s2:")
    # print(s2)

    print("=" * 40)

    print("Before alive to dead:")
    print(binary)
    print("before alive to dead s1:")
    print(s1)
    print("before alive to dead s2:")
    print(s2)

    binary.alive_to_dead(alive_neighbors, color1_neighbors, color2_neighbors, s1, s2)

    print("After alive to dead:")
    print(binary)
    print("After alive to dead s1:")
    print(s1)
    print("After alive to dead s2:")
    print(s2)

    print("=" * 40)

    print("Before dead to alive:")
    print(binary)
    print("before dead to alive s1:")
    print(s1)
    print("before dead to alive s2:")
    print(s2)

    binary.dead_to_alive(
        dead_neighbors, color1_dead_neighbors, color2_dead_neighbors, s1, s2
    )

    print("After dead to alive:")
    print(binary)
    print("After dead to alive s1:")
    print(s1)
    print("After dead to alive s2:")
    print(s2)


if __name__ == "__main__":
    # test_row_list()
    # test_life_list()
    # test_insert_many()
    # test_copy_life_list()
    # test_get_neighbor_count()
    # test_get_dead_neighbor_counts()
    # test_get_all_neighbor_counts()
    # test_dead_neighbors_filter()
    test_dead_alive()
