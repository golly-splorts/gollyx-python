import golly_python
import unittest
from golly_python.linkedlists import (
    ListBase,
    SortedRowList,
    LifeList
)


class ListsTest(unittest.TestCase):

    def test_list_base_constructor(self):
        lb = ListBase()
        self.assertEqual(lb.length(), 0)
    
    def test_sorted_row_list(self):
        srl = SortedRowList(151, 10)
        srl.insert(155)
        srl.insert(154)
        srl.insert(152)
        srl.insert(-17)
        srl.insert(-20)
        srl.insert(-4)
        srl.insert(152)
        srl.insert(153)
        srl.insert(152)

        self.assertEqual(srl.length(), 9)

        self.assertEqual(srl.head(), 10)
        self.assertTrue(srl.contains(151))
        self.assertTrue(srl.contains(152))
        self.assertTrue(srl.contains(153))
        self.assertTrue(srl.contains(154))
        self.assertTrue(srl.contains(155))

    def test_life_list(self):
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
        self.assertEqual(ll.live_count(), 12)

        # Test that insert duplicates does not increment count
        ll.insert(1, 42)
        ll.insert(2, 42)
        self.assertEqual(ll.live_count(), 12)

        # Test contains() method
        self.assertTrue(ll.contains(155, 12))
        self.assertFalse(ll.contains(12, 155))

        self.assertTrue(ll.contains(151, 10))
        self.assertFalse(ll.contains(10, 151))

        self.assertFalse(ll.contains(150, 10))
        self.assertFalse(ll.contains(10, 150))

        # Test removal
        result = ll.remove(155, 12)
        self.assertTrue(result)
        self.assertFalse(ll.contains(155, 12))
        self.assertEqual(ll.live_count(), 11)

        result = ll.remove(150, 10)
        self.assertFalse(result)
        self.assertFalse(ll.contains(150, 10))
        self.assertEqual(ll.live_count(), 11)

    def test_sorted_row_list_insert_many(self):
        srl = SortedRowList(10)
        srl.insert(155)
        srl.insert(154)
        srl.insert(152)
        srl.insert(-17)
        srl.insert(-20)
        srl.insert(-4)

        self.assertEqual(srl.length(), 7)

        self.assertFalse(srl.contains(10))
        self.assertFalse(srl.contains(200))

        self.assertTrue(srl.contains(-20))
        self.assertTrue(srl.contains(152))
        self.assertTrue(srl.contains(154))

        srl.insert_many_sorted([88, 152, 181])

        self.assertEqual(srl.length(), 9)

        self.assertTrue(srl.contains(-20))
        self.assertTrue(srl.contains(88))
        self.assertTrue(srl.contains(152))
        self.assertTrue(srl.contains(154))
        self.assertTrue(srl.contains(181))

        srl.insert_many_sorted([152, 153, 154])
        
        self.assertEqual(srl.length(), 10)

        self.assertTrue(srl.contains(-20))
        self.assertTrue(srl.contains(88))
        self.assertTrue(srl.contains(152))
        self.assertTrue(srl.contains(153))
        self.assertTrue(srl.contains(154))
        self.assertTrue(srl.contains(181))

    def test_copy_life_list(self):
        l1a = LifeList()
        for i in range(10):
            l1a.insert(90, 100 + i)
            l1a.insert(91, 100 + i)
            l1a.insert(92, 100 + i)
            l1a.insert(93, 100 + i)

        self.assertTrue(l1a.contains(90, 100))
        self.assertTrue(l1a.contains(90, 101))
        self.assertTrue(l1a.contains(90, 102))

        self.assertTrue(l1a.contains(93, 100))
        self.assertTrue(l1a.contains(93, 101))
        self.assertTrue(l1a.contains(93, 102))

        l1b = LifeList()
        for i in range(10):
            l1b.insert(90, 180 + i)
            l1b.insert(91, 180 + i)
            l1b.insert(92, 180 + i)
            l1b.insert(93, 180 + i)

        self.assertTrue(l1b.contains(90, 180))
        self.assertTrue(l1b.contains(90, 181))
        self.assertTrue(l1b.contains(90, 182))

        self.assertTrue(l1b.contains(93, 180))
        self.assertTrue(l1b.contains(93, 181))
        self.assertTrue(l1b.contains(93, 182))

        l1c = LifeList()
        for i in range(10):
            l1c.insert(88 + i, 170)

        self.assertTrue(l1c.contains(88, 170))
        self.assertTrue(l1c.contains(89, 170))
        self.assertTrue(l1c.contains(90, 170))

        l2 = LifeList()
        l2.insert(90, 170)
        l2.insert(91, 171)

        self.assertTrue(l2.contains(90, 170))
        self.assertTrue(l2.contains(91, 171))

        l2.copy_points(l1a)
        l2.copy_points(l1b)
        l2.copy_points(l1c)

        self.assertTrue(l2.contains(90, 100))
        self.assertTrue(l2.contains(90, 101))
        self.assertTrue(l2.contains(90, 102))

        self.assertTrue(l2.contains(93, 100))
        self.assertTrue(l2.contains(93, 101))
        self.assertTrue(l2.contains(93, 102))

        self.assertTrue(l2.contains(90, 180))
        self.assertTrue(l2.contains(90, 181))
        self.assertTrue(l2.contains(90, 182))

        self.assertTrue(l2.contains(93, 180))
        self.assertTrue(l2.contains(93, 181))
        self.assertTrue(l2.contains(93, 182))

        self.assertTrue(l2.contains(88, 170))
        self.assertTrue(l2.contains(89, 170))
        self.assertTrue(l2.contains(90, 170))

        self.assertTrue(l2.contains(90, 170))
        self.assertTrue(l2.contains(91, 171))

    ### def test_get_dead_neighbor_counts():
    ### 
    ###     # i = LifeList()
    ###     # i.insert(1, 1)
    ###     # print("State:")
    ###     # print(i)
    ###     # print("Dead neighbor counts:")
    ###     # print(i.get_dead_neighbor_counts())
    ### 
    ###     # print("")
    ### 
    ###     # Vertical line
    ###     # dead neighbr count should be 3 for two cells:
    ###     # (0, 2)
    ###     # (2, 2)
    ###     j = LifeList()
    ###     j.insert(1, 1)
    ###     j.insert(1, 2)
    ###     j.insert(1, 3)
    ###     print("State:")
    ###     print(j)
    ###     print("Dead neighbor counts:")
    ###     print(j.get_dead_neighbor_counts())
    ###     print("Should contain the entry 2: [0: 3, 2: 3]")


    def test_get_all_neighbor_counts(self):
    
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
    
        #tests/test_lists.py::ListsTest::test_get_all_neighbor_counts
        # {2: [0: 3, 2: 3], 0: [0: 1, 1: 1, 2: 1], 1: [0: 2, 2: 2], 3: [0: 2, 2: 2], 4: [0: 1, 1: 1, 2: 1], 16: [9: 3, 11: 3], 14: [9: 1, 10: 1, 11: 1], 15: [9: 2, 11: 2], 17: [9: 2, 11: 2], 18: [9: 1, 10: 1, 11: 1]}

        # Dead neighbors

        self.assertEqual(dead_neighbors.count(0, 2), 3)
        self.assertEqual(dead_neighbors.count(2, 2), 3)

        self.assertEqual(dead_neighbors.count(0, 0), 1)
        self.assertEqual(dead_neighbors.count(1, 0), 1)
        self.assertEqual(dead_neighbors.count(2, 0), 1)

        self.assertEqual(dead_neighbors.count(0, 1), 2)
        self.assertEqual(dead_neighbors.count(2, 1), 2)

        self.assertEqual(dead_neighbors.count(0, 3), 2)
        self.assertEqual(dead_neighbors.count(2, 3), 2)

        self.assertEqual(dead_neighbors.count(0, 4), 1)
        self.assertEqual(dead_neighbors.count(1, 4), 1)
        self.assertEqual(dead_neighbors.count(2, 4), 1)

        # Alive neighbors

        self.assertEqual(alive_neighbors.count(1, 1), 1)
        self.assertEqual(alive_neighbors.count(1, 2), 2)
        self.assertEqual(alive_neighbors.count(1, 3), 1)

        self.assertEqual(alive_neighbors.count(10, 15), 1)
        self.assertEqual(alive_neighbors.count(10, 16), 2)
        self.assertEqual(alive_neighbors.count(10, 17), 1)

        # color 1 alive neighbors

        #print(color1_neighbors)
        # {2: [1: 2], 15: [10: 1], 17: [10: 1]}
        self.assertEqual(color1_neighbors.count(1, 2), 2)
        self.assertEqual(color1_neighbors.count(10, 15), 1)
        self.assertEqual(color1_neighbors.count(10, 17), 1)

        #print(color2_neighbors)
        #{1: [1: 1], 3: [1: 1], 16: [10: 2]}
        self.assertEqual(color2_neighbors.count(1, 1), 1)
        self.assertEqual(color2_neighbors.count(1, 3), 1)
        self.assertEqual(color2_neighbors.count(10, 16), 2)
    
    ### def test_dead_neighbors_filter():
    ### 
    ###     binary = LifeList()
    ###     binary.insert(1, 1)
    ###     binary.insert(1, 2)
    ###     binary.insert(1, 3)
    ###     binary.insert(10, 15)
    ###     binary.insert(10, 16)
    ###     binary.insert(10, 17)
    ### 
    ###     s1 = LifeList()
    ###     s1.insert(1, 1)
    ###     s1.insert(10, 16)
    ###     s1.insert(1, 3)
    ###     s2 = LifeList()
    ###     s2.insert(10, 15)
    ###     s2.insert(1, 2)
    ###     s2.insert(10, 17)
    ### 
    ###     (
    ###         dead_neighbors,
    ###         color1_dead_neighbors,
    ###         color2_dead_neighbors,
    ###         alive_neighbors,
    ###         color1_neighbors,
    ###         color2_neighbors,
    ###     ) = binary.get_all_neighbor_counts(s1, s2)
    ### 
    ###     dead_neighbors.filter(3, 3)
    ###     print(dead_neighbors)
    ### 
    ### 
    ### def test_dead_alive():
    ### 
    ###     binary = LifeList()
    ###     binary.insert(1, 1)
    ###     binary.insert(1, 2)
    ###     binary.insert(1, 3)
    ###     binary.insert(10, 15)
    ###     binary.insert(10, 16)
    ###     binary.insert(10, 17)
    ### 
    ###     s1 = LifeList()
    ###     s1.insert(1, 1)
    ###     s1.insert(10, 16)
    ###     s1.insert(1, 3)
    ###     s2 = LifeList()
    ###     s2.insert(10, 15)
    ###     s2.insert(1, 2)
    ###     s2.insert(10, 17)
    ### 
    ###     print("Before:")
    ###     print(binary)
    ###     print("Before s1:")
    ###     print(s1)
    ###     print("Before s2:")
    ###     print(s2)
    ### 
    ###     # print("="*40)
    ### 
    ###     # print("Before get all neighbor counts:")
    ###     # print(binary)
    ###     # print("before get all neighbor counts s1:")
    ###     # print(s1)
    ###     # print("before get all neighbor counts s2:")
    ###     # print(s2)
    ### 
    ###     (
    ###         dead_neighbors,
    ###         color1_dead_neighbors,
    ###         color2_dead_neighbors,
    ###         alive_neighbors,
    ###         color1_neighbors,
    ###         color2_neighbors,
    ###     ) = binary.get_all_neighbor_counts(s1, s2)
    ### 
    ###     # print("After get all neighbor counts:")
    ###     # print(binary)
    ###     # print("after get all neighbor counts s1:")
    ###     # print(s1)
    ###     # print("after get all neighbor counts s2:")
    ###     # print(s2)
    ### 
    ###     print("=" * 40)
    ### 
    ###     print("Before alive to dead:")
    ###     print(binary)
    ###     print("before alive to dead s1:")
    ###     print(s1)
    ###     print("before alive to dead s2:")
    ###     print(s2)
    ### 
    ###     binary.alive_to_dead(alive_neighbors, color1_neighbors, color2_neighbors, s1, s2)
    ### 
    ###     print("After alive to dead:")
    ###     print(binary)
    ###     print("After alive to dead s1:")
    ###     print(s1)
    ###     print("After alive to dead s2:")
    ###     print(s2)
    ### 
    ###     print("=" * 40)
    ### 
    ###     print("Before dead to alive:")
    ###     print(binary)
    ###     print("before dead to alive s1:")
    ###     print(s1)
    ###     print("before dead to alive s2:")
    ###     print(s2)
    ### 
    ###     binary.dead_to_alive(
    ###         dead_neighbors, color1_dead_neighbors, color2_dead_neighbors, s1, s2
    ###     )
    ### 
    ###     print("After dead to alive:")
    ###     print(binary)
    ###     print("After dead to alive s1:")
    ###     print(s1)
    ###     print("After dead to alive s2:")
    ###     print(s2)
    ### 
    ### 
    ### def test_twostep():
    ### 
    ###     binary = LifeList()
    ###     binary.insert(1, 1)
    ###     binary.insert(1, 2)
    ###     binary.insert(1, 3)
    ###     binary.insert(10, 15)
    ###     binary.insert(10, 16)
    ###     binary.insert(10, 17)
    ### 
    ###     s1 = LifeList()
    ###     s1.insert(1, 1)
    ###     s1.insert(10, 16)
    ###     s1.insert(1, 3)
    ### 
    ###     s2 = LifeList()
    ###     s2.insert(10, 15)
    ###     s2.insert(1, 2)
    ###     s2.insert(10, 17)
    ### 
    ###     print("="*40)
    ### 
    ###     print("Before first step:")
    ###     print(binary)
    ###     print(s1)
    ###     print(s2)
    ### 
    ###     (
    ###         dead_neighbors,
    ###         color1_dead_neighbors,
    ###         color2_dead_neighbors,
    ###         alive_neighbors,
    ###         color1_neighbors,
    ###         color2_neighbors,
    ###     ) = binary.get_all_neighbor_counts(s1, s2)
    ### 
    ###     binary.alive_to_dead(alive_neighbors, color1_neighbors, color2_neighbors, s1, s2)
    ### 
    ###     binary.dead_to_alive(
    ###         dead_neighbors, color1_dead_neighbors, color2_dead_neighbors, s1, s2
    ###     )
    ### 
    ###     print("="*40)
    ### 
    ###     print("After first step:")
    ###     print(binary)
    ###     print(s1)
    ###     print(s2)
    ### 
    ###     (
    ###         dead_neighbors,
    ###         color1_dead_neighbors,
    ###         color2_dead_neighbors,
    ###         alive_neighbors,
    ###         color1_neighbors,
    ###         color2_neighbors,
    ###     ) = binary.get_all_neighbor_counts(s1, s2)
    ### 
    ###     binary.alive_to_dead(alive_neighbors, color1_neighbors, color2_neighbors, s1, s2)
    ### 
    ###     binary.dead_to_alive(
    ###         dead_neighbors, color1_dead_neighbors, color2_dead_neighbors, s1, s2
    ###     )
    ### 
    ###     print("="*40)
    ### 
    ###     print("After second step:")
    ###     print(binary)
    ###     print(s1)
    ###     print(s2)
