class EmptyListError(Exception):
    pass


class MovingAvgNode(object):
    next_node = None
    data: float = None

    def __init__(self, data: float):
        self.data = data


class MovingAvgList(object):
    """
    Implement a circular linked list to handle a moving average calculation.

    This class uses a single pointer to the back of the circular linked list.
    To get the front of the list, use back.next.
    """
    size: int = 0
    back_node: MovingAvgNode = None

    def __init__(self):
        pass

    def length(self):
        return self.size

    def index(self, ix):
        if ix < 0 or ix >= self.size:
            raise IndexError(f"Error: requested index {ix} invalid for list of size {self.size}")
        runner = self.back_node.next_node
        for i in range(ix):
            runner = runner.next_node
        return runner.data

    def sum(self):
        summ = 0.0
        c = 0
        if self.size == 0:
            return 0
        runner = self.back_node.next_node
        while runner != self.back_node.next_node or c==0:
            summ += runner.data
            runner = runner.next_node
            c += 1

        return summ

    def avg(self):
        if self.size > 0:
            return self.sum()/self.size

    def push_back(self, data):
        """Append data to the back of the list"""

        if self.back_node is None:
            # Empty list
            node = MovingAvgNode(data)
            node.next_node = node
            self.back_node = node
            self.size += 1

        else:
            # Create a new back node
            node = MovingAvgNode(data)
            # New back node's next node points to front node
            node.next_node = self.back_node.next_node
            # Old back node's next node points to new back node
            self.back_node.next_node = node
            # Back node pointer points to new back node
            self.back_node = node
            self.size += 1

    def push_back_pop_front(self, value):
        """Rotate the circular list to pop front and push back"""
        # Slide the back node pointer up by one
        self.back_node = self.back_node.next_node
        # Replace the value of the new back node
        old_value = self.back_node.data
        self.back_node.data = value
        return old_value


if __name__=="__main__":
    m = MovingAvgList()
    assert m.length()==0
    assert m.sum() < 1e-12
    assert m.avg() is None

    m.push_back(10)
    m.push_back(20)
    m.push_back(30)
    assert m.size==3
    assert m.length()==3
    assert m.sum()==60
    assert abs(m.avg()-20) < 1e-12

    m.push_back_pop_front(40)
    m.push_back_pop_front(50)
    m.push_back_pop_front(60)
    assert m.length()==3
    assert m.sum()==150
    assert abs(m.avg()-50) < 1e-12

    assert m.index(0)==40
    assert m.index(1)==50
    assert m.index(2)==60
