class NodeBase(object):
    data = None
    next_node = None

    def __init__(self, data):
        self.data = data


class ListBase(object):
    size: int = 0
    front_node: NodeBase = None

    def __init__(self):
        pass

    def length(self):
        return self.size


class ListBaseIterator(object):
    def __init__(self, obj):
        self.obj = obj

    def __iter__(self):
        return self

    def next(self):
        runner = self.obj.front_node
        while runner != None:
            yield runner.data
            runner = runner.next_node
        raise StopIteration()


class LocationNode(NodeBase):
    data: int = 0


class SortedRowList(object):
    """
    Store one row in a game of life.
    This stores the coordinates of each cell in the form

    [ y  x1  x2  x3  ... ]

    where x1, x2, x3 are in sorted order. Example:

    [ 100 15 16 19 ]

    represents the three cells (15,100) (16,100) (19,100)
    """

    size: int = 0
    front_node: LocationNode = None
    back_node: LocationNode = None

    def __init__(self, x, y):
        self.insert(y)
        self.insert(x)

    def __repr__(self):
        agg = "["
        runner = self.front_node
        c = 0
        while runner != None:
            if c > 0:
                agg += ", "
            agg += str(runner.data)
            runner = runner.next_node
            c += 1
        agg += "]"
        return agg

    def head(self):
        if self.size > 0:
            return self.front_node.data

    def insertion_index(self, x):
        """
        Given an element x, return a pointer to the insertion index
        (the Node preceding the spot where the new Node would go).
        If x is in the list, this returns the Node preceding it.
        """
        if self.size == 0:
            return None

        elif self.size == 1:
            return self.front_node

        else:
            leader = self.front_node.next_node
            lagger = self.front_node
            while leader != None and x > leader.data:
                lagger = leader
                leader = leader.next_node
            return lagger

    def find(self, x):
        """
        Given an element x, return a pointer to the Node for that element, or None.
        """
        if self.size == 0 or self.size == 1:
            return None

        node = self.insertion_index(x)
        if node.next_node.data == x:
            return node
        else:
            return None

    def contains(self, x):
        if self.find(x) is None:
            return False
        else:
            return True

    def insert(self, x):
        if self.size == 0:
            # Handle empty list case first:
            # Create new Node and set it as the front and the back
            ynode = LocationNode(x)
            self.front_node = ynode
            self.back_node = ynode
            self.size += 1
            return True

        else:
            # There is already at least 1 element in the list.
            # First element is always y. Maintain values following in sorted order.
            ii = self.insertion_index(x)

            if (ii.next_node is not None) and (ii.next_node.data == x):
                # Already in list
                return False
            else:
                # insert x into the list after the insertion index node
                front = ii
                back = ii.next_node
                middle = LocationNode(x)
                if back is None:
                    # Appending to end of list, update back pointer as well
                    front.next_node = middle
                    self.back_node = middle
                    self.size += 1
                    return True
                else:
                    front.next_node = middle
                    middle.next_node = back
                    self.size += 1
                    return True

    def remove(self, x):
        if self.size == 0 or self.size == 1:
            return False

        ii = self.insertion_index(x)
        if (ii.next_node is not None) and (ii.next_node.data == x):
            # Found it
            front = ii
            back = ii.next_node.next_node
            if back is None:
                # The noded we are removing is the back of the list, update back pointer
                self.back_node = front
            front.next_node = back
            self.size -= 1
            return True
        else:
            # x is not in the list
            return False

    def empty(self):
        """Boolean: have all nodes been removed from list"""
        return self.size == 0

    def emptyx(self):
        """Boolean: have all x values been removed from list"""
        return self.size == 0 or self.size == 1


class RowNode(NodeBase):
    data: SortedRowList = 0


class LifeList(object):
    """
    List Life data structure.

    This stores a list of RowLists, so the data looks like
    [
        [ y1  x11  x12  x13  ... ],
        [ y2  x21  x22  x23  ... ],
        [ y3  x31  x32  x33  ... ]
    ]
    """

    size: int = 0
    ncells: int = 0
    front_node: RowNode = None

    def __repr__(self):
        agg = "[\n"
        runner = self.front_node
        while runner != None:
            agg += "    "
            agg += str(runner.data)
            agg += ",\n"
            runner = runner.next_node
        agg += "]"
        return agg

    def length(self):
        return self.size

    def live_count(self):
        return self.ncells

    def copy_points(self, other_lifelist):
        """
        Copy every point in another LifeList into this LifeList.
        Return a boolean: were any points copied.
        This method could be more efficient, but right now we just wanna get something working.
        """
        if other_lifelist.size == 0:
            return False

        else:
            response = False
            other_yrunner = other_lifelist.front_node
            while other_yrunner != None: 
                row = other_yrunner.data
                y = row.head()
                other_xrunner = row.front_node.next_node
                while other_xrunner != None:
                    x = other_xrunner.data
                    result = self.insert(x, y)
                    response = response or result
                    other_xrunner = other_xrunner.next_node
                other_yrunner = other_yrunner.next_node
            return response

    def insertion_index(self, y):
        """
        Given a y value, return the insertion index where
        a row with that y value would go.
        """
        if self.size == 0:
            return None

        elif self.size == 1:
            return self.front_node

        else:
            leader = self.front_node.next_node
            lagger = self.front_node
            while leader != None and y > leader.data.head():
                lagger = leader
                leader = leader.next_node
            return lagger

    def _find(self, y):
        """Given a y value, return a pointer to the row for that element, or None"""
        node = self.insertion_index(y)
        if node.data.head() == y:
            return node
        else:
            return None

    def _contains(self, y):
        if self._find(y):
            return True
        else:
            return False

    def find(self, x, y):
        """Given an (x, y) coordinate, return a pointer to the LocationNode in the RowNode, or None"""
        ypointer = self._find(y)
        if ypointer is not None:
            row = ypointer.data
            xpointer = row.find(x)
            if xpointer is not None:
                return xpointer
        return None

    def contains(self, x, y):
        if self.find(x, y):
            return True
        else:
            return False

    def insert(self, x, y):
        if self.size == 0:
            # Handle empty list case first:
            # Create new Node and set it as the front
            row = SortedRowList(x, y)
            self.front_node = RowNode(row)
            self.size += 1
            self.ncells += 1
            return True

        elif (self.size >= 1) and (self.front_node.data.head()==y):
            # Handle this case explicitly, to avoid the need for a ghost leader node.
            # In this case, the insertion index would be the ghost node before the front_node.
            this_row = self.front_node
            # y already has a row, insert x into it
            if this_row.data.insert(x):
                self.ncells += 1
                return True
            else:
                return False

        else:
            # There is already at least one row in the list.
            ii = self.insertion_index(y)

            if (ii.next_node is not None) and (ii.next_node.data.head() == y):
                this_row = ii.next_node
                # y already has a row, insert x into it
                if this_row.data.insert(x):
                    self.ncells += 1
                    return True
                else:
                    return False
            else:
                # y does not have a row yet
                # insert y into the list after the insertion index node
                front = ii
                back = ii.next_node
                row = SortedRowList(x, y)
                middle = RowNode(row)
                front.next_node = middle
                middle.next_node = back
                self.size += 1
                self.ncells += 1
                return True

    def remove(self, x, y):
        if self.size == 0:
            return False

        ii = self.insertion_index(y)
        if (ii.next_node is not None) and (ii.next_node.data.head() == y):
            # Found it
            rowlist = ii.next_node.data
            remove_worked = rowlist.remove(x)
            if remove_worked:
                self.ncells -= 1
                if rowlist.emptyx():
                    # This was the last x value in the row, so remove this row from listlife
                    front = ii
                    back = ii.next_node.next_node
                    front.next_node = back
                    self.size -= 1
            return remove_worked
        else:
            # y is not in the list
            return False

    def get_neighbor_count(self, x, y):
        """Count the number of neighbors of cell (x,y) in this state."""
        if self.size==0:
            return 0

        neighborcount = 0

        aboverownode = self._find(y-1)
        if aboverownode:
            aboverow = aboverownode.data
            ii = aboverow.insertion_index(x)
            if ii.data == (x-1):
                neighborcount += 1
            if ii.next_node != None and ii.next_node.data == x:
                neighborcount += 1
                if ii.next_node.next_node != None and ii.next_node.next_node.data == (x+1):
                    neighborcount += 1

        thisrownode = self._find(y)
        if thisrownode:
            thisrow = thisrownode.data
            ii = thisrow.insertion_index(x)
            # Verify the cell itself is here
            if ii.next_node != None and ii.next_node.data == x:
                # Don't increment neighborcount for cell tiself
                if ii.data == (x-1):
                    neighborcount += 1
                if ii.next_node.next_node != None and ii.next_node.next_node.data == (x+1):
                    neighborcount += 1

        belowrownode = self._find(y+1)
        if belowrownode:
            belowrow = belowrownode.data
            ii = belowrow.insertion_index(x)
            if ii.data == (x-1):
                neighborcount += 1
            if ii.next_node != None and ii.next_node.data == x:
                neighborcount += 1
                if ii.next_node.next_node != None and ii.next_node.next_node.data == (x+1):
                    neighborcount += 1

        return neighborcount


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


def test_copy_life_list():
    import random
    print("Life List 1:")
    l1 = LifeList()
    for i in range(70):
        l1.insert(random.randint(10,15), random.randint(100,150))
    print(l1)
    print(l1.live_count())

    l2 = LifeList()
    l2.insert(10, 98)
    l2.insert(11, 99)

    print("Life List 2 before copy:")
    print(l2)
    print(l2.live_count())

    l2.copy_points(l1)

    print("Life List 2 after copy:")
    print(l2)
    print(l2.live_count())


if __name__ == "__main__":
    #test_row_list()
    #test_life_list()
    test_copy_life_list()
