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
        leader = self.front_node.next_node
        lagger = self.front_node
        while leader != None and x > leader.data:
            lagger = leader
            leader = leader.next_node
        if leader == None:
            # Reached end of list without finding x
            return lagger
        elif leader.data == x:
            # x value is in the list
            return leader
        else:
            # x value is not in the list
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
        node = self.find(x)
        if node is not None:
            return True
        else:
            return False

    def insert(self, value):

        # The first element into the list is always y value.
        # This list will maintain the values that follow in sorted order.
        if self.size==0:
            # Create the new node
            ynode = LocationNode(value)
            # New node is both front and back
            self.front_node = ynode
            self.back_node = ynode
            self.size += 1
            return True
        else:
            # The first element into the list is always y,
            # so maintain values that follow in sorted order.
            if self.front_node.next_node == None:
                # There are no other x values
                caboose = LocationNode(value)
                self.back_node.next_node = caboose
                self.back_node = caboose
                self.size += 1
                return True

            else:
                # Start the leader on the second element
                leader = self.front_node.next_node
                lagger = self.front_node
                while (leader != None) and (value > leader.data):
                    leader = leader.next_node
                    lagger = lagger.next_node

                if leader == None:
                    # Reached end without finding data, so append to end
                    caboose = LocationNode(value)
                    self.back_node.next_node = caboose
                    self.back_node = caboose
                    self.size += 1
                    return True
                elif leader.data == value:
                    # Data is already in list, return without inserting
                    return False
                else:
                    # Insert new data between leader and lagger
                    middle = LocationNode(value)
                    lagger.next_node = middle
                    middle.next_node = leader
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

    def find(self, x, y):
        """Given a coordinate (x, y), return a pointer to the location node, or None"""
        if self.size==0:
            return None
        else:           
            # Start the leader on the first element
            leader = self.front_node
            lagger = None
            while (leader != None) and (y > leader.data.head()):
                lagger = leader
                leader = leader.next_node
            if leader == None:
                # Reached end without finding y, so does not contain
                return None
            elif y == leader.data.head():
                # y matches an existing row, check if that row contains x
                return leader.data.find(x)
            else:
                # Life list does not contain this y value
                return None

    def contains(self, x, y):
        if self.find(x, y):
            return True
        else:
            return False

    def insert(self, x, y):
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
    ll.insert(152, 10)
    ll.insert(153, 10)
    ll.insert(150, 11)
    ll.insert(152, 11)
    ll.insert(156, 12)
    ll.insert(149, 12)
    ll.insert(155, 12)
    print(ll)
    print('contains 155, 12 (should be true):')
    print(ll.contains(155,12))
    print('contains 12, 155 (should be false):')
    print(ll.contains(12,155))
    print('contains 151, 10 (should be true):')
    print(ll.contains(151,10))
    print('contains 150, 10 (should be false):')
    print(ll.contains(150,10))
