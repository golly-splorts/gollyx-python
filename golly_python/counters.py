class XCounterStore(object):
    """
    Small utilty class used by XYCounterStore
    to store counters for a set of x values.
    Wraps a hash map of x values to integer counts.
    """
    __slots__ = ['mapp']

    def __init__(self):
        self.mapp = dict()

    def __repr__(self):

        s = "["
        s += ", ".join([f"{j}: {self.mapp[j]}" for j in self.sorted_values()])
        s += "]"
        return s

    def accumulate(self, x):
        if x not in self.mapp:
            self.mapp[x] = 1
        else:
            self.mapp[x] += 1

    def filter(self, lo, hi):
        for x in list(self.mapp.keys()):
            if not (self.mapp[x] >= lo and self.mapp[x] <= hi):
                del self.mapp[x]

    def count(self, x):
        if x not in self.mapp:
            return 0
        else:
            return self.mapp[x]

    def sorted_values(self):
        return sorted(list(self.mapp.keys()))


class XYCounterStore(object):
    """
    Small utility class storing counters for (x,y) values.
    Wraps a hash map of y values to x counter stores.
    """
    __slots__ = ['mapp']

    def __init__(self):
        self.mapp = dict()

    def __repr__(self):
        return str(self.mapp)

    def accumulate(self, x, y):
        if y not in self.mapp:
            self.mapp[y] = XCounterStore()
        self.mapp[y].accumulate(x)

    def count(self, x, y):
        if y not in self.mapp:
            return 0

        xstore = self.mapp[y]
        if x not in xstore.mapp:
            return 0

        count = xstore.mapp[x]
        return count

    def sorted_values(self):
        return sorted(list(self.mapp.keys()))

    def sorted_xvalues(self, y):
        """Return a list of sorted x values for the given y"""
        if y not in self.mapp:
            return None

        xstore = self.mapp[y]
        return xstore.sorted_values()

    def filter(self, lo, hi):
        """Filter all counts in this XYCounterStore to values that are between lo and hi"""
        for y in list(self.mapp.keys()):
            self.mapp[y].filter(lo, hi)
            x_values = self.mapp[y].mapp
            if len(x_values) == 0:
                del self.mapp[y]


class DeadNeighborCounter(XYCounterStore):
    """
    Used to count the number of times a dead cell has been a neighbor
    of a live cell  (used in determining which cells come alive).
    Wraps a hash map of (x, y) locations to integer counters.
    """

    pass


class AliveNeighborCounter(XYCounterStore):
    """
    Used to count the number of live neighbors of a given live cell.
    """

    pass
