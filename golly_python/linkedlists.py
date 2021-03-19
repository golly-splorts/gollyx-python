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
        if self.size>0:
            return self.front_node.data

    def insertion_index(self, x):
        """
        Given an element x, return a pointer to the insertion index
        (the Node preceding the spot where the new Node would go)
        """
        if self.size==0:
            return None

        elif self.size==1:
            return self.front_node

        else:
            leader = self.front_node.next_node
            lagger = self.front_node
            while leader != None and x > leader.data:
                lagger = leader
                leader = leader.next_node
            if leader == None:
                # Reached end of list without finding x, return end of list
                return lagger
            elif leader.data == x:
                # x value is in the list, leader points to it
                return leader
            else:
                # x value is not in the list, leader and all following are higher
                return lagger

    def find(self, x):
        """
        Given an element x, return a pointer to the Node for that element, or None.
        """
        node = self.insertion_index(x)
        if node.data == x:
            return node
        else:
            return None

    def contains(self, x):
        if self.find(x) is None:
            return False
        else:
            return True

    def insert(self, x):
        if self.size==0:
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
            if ii.data == x:
                # x is already in this list
                return False
            else:
                # insert x into the list after the insertion index node
                front = ii
                back = ii.next_node
                middle = LocationNode(x)
                front.next_node = middle
                middle.next_node = back
                self.size += 1
                return True

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

    def insertion_index(self, y):
        """
        Given a y value, return the insertion index where
        a row with that y value would go.
        """
        if self.size==0:
            return None

        elif self.size==1:
            return self.front_node

        else:
            leader = self.front_node.next_node
            lagger = self.front_node
            while leader != None and y > leader.data.head():
                lagger = leader
                leader = leader.next_node
            if leader == None:
                # Reached end of list without finding x, return end of list
                return lagger
            elif leader.data.head() == y:
                # row for this y exists, leader points to it
                return leader
            else:
                # row for this y does not exist, leader and all following are higher
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
        if self.size==0:
            # Handle empty list case first:
            # Create new Node and set it as the front
            row = SortedRowList(x, y)
            self.front_node = RowNode(row)
            self.size += 1
            self.ncells += 1
            return True

        else:
            # There is already at least one row in the list.
            ii = self.insertion_index(y)
            if ii.data.head() == y:
                # y already has a row, insert x into it
                if ii.data.insert(x):
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

    def old_insert(self, x, y):
        if self.size==0:
            # Create a new row
            row = SortedRowList(x, y)
            self.front_node = RowNode(row)
            self.size += 1
            self.ncells += 1
            return True
        else:           
            # Start the leader on the first element
            leader = self.front_node
            lagger = None
            while (leader != None) and (y > leader.data.head()):
                lagger = leader
                leader = leader.next_node
            if leader == None:
                # Reached end without finding y, so append new RowNode
                row = SortedRowList(x, y)
                lagger.next_node = RowNode(row)
                self.size += 1
                self.ncells += 1
                return True
            elif y == leader.data.head():
                # Row for this y value already exists, insert into existing list
                if leader.data.insert(x):
                    self.ncells += 1
                    return True
                else:
                    return False
            else:
                # Insert new row between leader and lagger
                middle = SortedRowList(x, y)
                lagger.next_node = middle
                middle.next_node = leader
                self.size += 1
                self.ncells += 1
                return True

    def remove(self, x, y):
        if self.size==0:
            return False


if __name__=="__main__":

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

    print('contains 155, 12 (should be true):')
    print(ll.contains(155,12))
    print('contains 12, 155 (should be false):')
    print(ll.contains(12,155))
    print('contains 151, 10 (should be true):')
    print(ll.contains(151,10))
    print('contains 150, 10 (should be false):')
    print(ll.contains(150,10))
