class DeadCellCounter(object):
    def __init__(self):
        self.mapp = dict()

    def __repr__(self):
        return str(self.mapp)

    def add(self, x, y):
        key = str(x) + "," + str(y)
        if key not in self.mapp:
            self.mapp[key] = 1
        else:
            self.mapp[key] += 1

    def count(self, x, y):
        key = str(x) + "," + str(y)
        if key in self.mapp:
            return self.mapp[key]
        else:
            return 0


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
    head: bool = False


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
        The first element is always y, so elements never go at the front of the list.
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
        Given an element x, return a pointer to the Node for that element,
        or return None if the item is not in the list.
        (To get preceding node, use insertion_index)
        """
        if self.size == 0 or self.size == 1:
            return None

        node = self.insertion_index(x)
        if node is None:
            node = self.front_node

        if node.next_node is not None:
            if node.next_node.data == x:
                return node.next_node

        return None

    def contains(self, x):
        if self.find(x) is None:
            return False
        else:
            return True

    def insert(self, x):
        """Insert the given x location into the sorted list"""

        if self.size == 0:
            # Handle empty list case first:
            # Create new Node and set it as the front and the back
            ynode = LocationNode(x)
            ynode.head = True
            self.front_node = ynode
            self.back_node = ynode
            self.size += 1
            return True

        else:
            # There is already at least 1 element in the list.
            # First element is always y. Maintain values following in sorted order.
            ii = self.insertion_index(x)

            if ii.next_node is not None:
                if ii.next_node.data == x:
                    # Already in list
                    return False

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

        else:
            leader = self.front_node
            lagger = None
            while leader != None and y > leader.data.head():
                lagger = leader
                leader = leader.next_node
            return lagger

    def _find(self, y):
        """Given a y value, return a pointer to the row node for that y, or None"""
        if self.size == 0:
            return None

        node = self.insertion_index(y)
        if node is None:
            # Insertion index is at front, check if front contains element
            if self.front_node.data.head() == y:
                return self.front_node
            else:
                return None

        elif node.next_node is not None:
            if node.next_node.data.head() == y:
                return node.next_node

        return None

    def _contains(self, y):
        if self.size == 0:
            return False
        if self._find(y):
            return True
        else:
            return False

    def find(self, x, y):
        """Given an (x, y) coordinate, return a pointer to the LocationNode in the RowNode, or None"""
        if self.size == 0:
            return None

        ypointer = self._find(y)
        if ypointer is not None:
            row = ypointer.data
            xpointer = row.find(x)
            if xpointer is not None:
                return xpointer

        return None

    def contains(self, x, y):
        if self.size == 0:
            return False
        if self.find(x, y):
            return True
        else:
            return False

    def insert(self, x, y):
        """Insert the given (x, y) location into the correct list location"""

        if self.size == 0:
            # Handle empty list case first:
            # Create new Node and set it as the front
            row = SortedRowList(x, y)
            self.front_node = RowNode(row)
            self.size += 1
            self.ncells += 1
            return True

        elif (self.size >= 1) and (self.front_node.data.head() == y):
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

            if ii is None:
                # y does not have a row yet
                # if insertion index is none, the new row goes at the beginning
                row = SortedRowList(x, y)
                newfront = RowNode(row)
                oldfront = self.front_node
                newfront.next_node = oldfront
                self.front_node = newfront
                self.size += 1
                self.ncells += 1

            elif (ii.next_node is not None) and (ii.next_node.data.head() == y):
                this_row = ii.next_node
                # y already has a row in this list, insert x into it
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
        if (ii is None) and (self.front_node.data.head() == y):
            # y goes at the front of the list, and row exists already
            rowlist = self.front_node.data
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

        elif (ii.next_node is not None) and (ii.next_node.data.head() == y):
            # Found it in the list
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
        """Count the number of neighbors for cell (x,y)"""
        if self.size == 0:
            return 0

        neighborcount = 0

        # Find where above row should go
        aboveii = self.insertion_index(y - 1)
        if aboveii is None:
            aboverow = self.front_node.data
        else:
            if aboveii.next_node is None:
                # There is no above cell here, so we have no more points of interest
                return neighborcount
            else:
                aboverow = aboveii.next_node.data

        # Check if above row is actually y-1
        if aboverow.head() == (y - 1):

            # if x-1 is here, it has to be at the insertion index for x
            abovexii = aboverow.insertion_index(x)
            # Note: the .head check is True when abovexii.data is a y coordinate, checking x coordinates only
            if abovexii.data == (x - 1) and abovexii.head is False:
                neighborcount += 1

            # if x insertion index is at end of list, we are done with above row
            if abovexii.next_node is not None:
                # only advance the insertion index if we find x
                if abovexii.next_node.data == x:
                    neighborcount += 1
                    abovexii = abovexii.next_node
                if abovexii.next_node is not None:
                    if abovexii.next_node.data == (x + 1):
                        neighborcount += 1

        # Find where middle row should go
        if aboveii is None:
            if aboverow.head() == (y - 1):
                middleii = self.front_node
            else:
                middleii = None
        else:
            middleii = aboveii.next_node

        if middleii is None:
            middlerow = self.front_node.data
        else:
            if middleii.next_node is None:
                # Recall that middleii points to above row, so if next node is none, we have no middle row
                # That means we have no points of interest
                return neighborcount
            else:
                middlerow = middleii.next_node.data

        # Check if middle row is actually y (this should always succeed...)
        if middlerow.head() == y:

            # if x-1 is here, it is at insertion index for x
            middlexii = middlerow.insertion_index(x)
            if middlexii.data == (x - 1) and middlexii.head is False:
                neighborcount += 1

            # if x insertion index at end of list, done with row
            if middlexii.next_node is not None:
                # only advance insertion index if find x
                if middlexii.next_node.data == x:
                    # don't increment neighborcount for cell itself
                    middlexii = middlexii.next_node
                if middlexii.next_node is not None:
                    if middlexii.next_node.data == (x + 1):
                        neighborcount += 1

        # Find where bottom row should go
        if middleii is None:
            # middle row is always present
            # if the middle insertion index is none, the middle row is the first RowNode
            # that means the bottom row goes after the first RowNode
            bottomii = self.front_node
        else:
            # this is guaranteed not to be None, b/c of return statement above
            bottomii = middleii.next_node

        if bottomii.next_node is None:
            # There is no bottom row, we are done
            return neighborcount
        else:
            bottomrow = bottomii.next_node.data

        # Check if bottom row is actually y+1
        if bottomrow.head() == (y + 1):

            bottomxii = bottomrow.insertion_index(x)
            if bottomxii.data == (x - 1) and bottomxii.head is False:
                neighborcount += 1

            # if x insertion index at end of list, done with row
            if bottomxii.next_node is not None:
                # only advance insertion index if find x
                if bottomxii.next_node.data == x:
                    neighborcount += 1
                    bottomxii = bottomxii.next_node
                if bottomxii.next_node is not None:
                    if bottomxii.next_node.data == (x + 1):
                        neighborcount += 1

        return neighborcount

    def get_dead_neighbor_counts(self):
        dead_neighbors = DeadCellCounter()

        if self.size == 0:
            return dead_neighbors

        if self.size == 1:
            stencily_lag = None
            stencily_middle = self.front_node
            stencily_lead = stencily_middle.next_node
        else:
            stencily_lag = self.front_node
            stencily_middle = stencily_lab.next_node
            stencily_lead = stencily_middle.next_node

        while stencily_middle is not None:

            middlerow = stencily_middle.data
            y = middlerow.head()

            # Set stencil locations for this row
            stencilx_lag = middlerow.front_node
            stencilx_middle = stencilx_lag.next_node
            if stencilx_middle.next_node is not None:
                stencilx_lead = stencilx_middle.next_node
            else:
                stencilx_lead = None
            assert stencilx_middle is not None

            while stencilx_middle is not None:

                x = stencilx_middle.data

                # Deal with above (lead) row
                if stencily_lead is None or stencily_lead.data.head() != y + 1:
                    # Row for y+1 is missing
                    # Add (x-1, y+1), (x, y+1), (x+1, y+1) to deadcellcounter
                    dead_neighbors.add(x - 1, y + 1)
                    dead_neighbors.add(x, y + 1)
                    dead_neighbors.add(x + 1, y + 1)
                else:
                    # Scan lead row
                    aboverow = stencily_lead.data
                    abovexii = aboverow.insertion_index(x)
                    if not (abovexii.data == (x - 1) and abovexii.head is False):
                        # We do not have cell (x-1, y+1) in this list
                        dead_neighbors.add(x - 1, y + 1)

                    # if x insertion index is at end of list, we are done with row
                    if abovexii.next_node is not None:
                        # only advance insertion index if we find x
                        if not abovexii.next_node.data == x:
                            # We do not have cell (x, y+1) in this list
                            dead_neighbors.add(x, y + 1)
                        else:
                            # We do have cell (x, y+1) in this list, so advance the insertion index yb 1
                            abovexii = abovexii.next_node
                        if abovexii.next_node is not None:
                            if not abovexii.next_node.data == (x + 1):
                                # We do not have cell (x+1, y+1)
                                dead_neighbors.add(x + 1, y + 1)

                # Deal with below (lag) row
                if stencily_lag is None or stencily_lag.data.head() != y - 1:
                    # Add cell (x-1, y-1), (x, y-1), (x+1, y-1) to deadcellcounter
                    dead_neighbors.add(x - 1, y - 1)
                    dead_neighbors.add(x, y - 1)
                    dead_neighbors.add(x + 1, y - 1)
                else:
                    # Scan lag row
                    belowrow = stencily_lag.data
                    belowxii = belowrow.insertion_index(x)
                    if not (belowxii.data == (x - 1) and belowxii.head is False):
                        # We do not have cell (x-1, y-1) in this list
                        dead_neighbors.add(x - 1, y - 1)

                    # if x insertion index is at end of list, we are done with row
                    if belowxii.next_node is not None:
                        if not belowxii.next_node.data == x:
                            dead_neighbors.add(x, y - 1)
                        else:
                            belowii = belowii.next_node
                        if belowxii.next_node is not None:
                            if not belowxii.next_node.data == (x + 1):
                                dead_neighbors.add(x + 1, y - 1)

                # Deal with this row
                # Scan middle row
                if not (
                    stencilx_lag.data == (x - 1) and stencilx_lag.data.head is False
                ):
                    # We do not have cell (x-1, y) in this list
                    dead_neighbors.add(x - 1, y)

                if stencilx_lead is None or stencilx_lead.data != (x + 1):
                    # We do not have cell (x+1, y) i this list
                    dead_neighbors.add(x + 1, y)

                # Increment pointers
                # If any x pointers left, increment x pointers
                stencilx_lag = stencilx_lag.next_node
                stencilx_middle = stencilx_middle.next_node
                if stencilx_lead is not None:
                    stencilx_lead = stencilx_lead.next_node

            # Advance y pointers
            stencily_lag = stencily_middle
            stencily_middle = stencily_middle.next_node
            if stencily_lead is not None:
                stencily_lead = stencily_lead.next_ndoe

        return dead_neighbors


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
    i = LifeList()
    i.insert(1, 1)
    print(i.get_dead_neighbor_counts())


if __name__ == "__main__":
    # test_row_list()
    # test_life_list()
    # test_copy_life_list()
    # test_get_neighbor_count()
    test_get_dead_neighbor_counts()
