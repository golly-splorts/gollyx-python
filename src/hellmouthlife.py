# Used to determine if two numbers are approximately equal
EQUALTOL = 1e-8

# Used to avoid dividing by zero
SMOL = 1e-12

# Dimension (in time) of time-average window
MAXDIM = 240


"""
hellmouthlife does its own thing

defines a stats class
which is where the moving avg calculated
update_moving_avg method

as opposed to rainbow or toroidal life
which defines how to update moving avg in the life class itself
"""


def lists_equal(a, b):
    if len(a) != len(b):
        return False
    for ia, ib in zip(a, b):
        if ia != ib:
            return False
    return True

def approx_equal(a, b, tol):
    return (abs(b - a) / abs(a + SMOL)) < tol


class EmptyListError(Exception):
    pass


class MovingAvgNode(object):
    next_node = None
    data: float = None

    def __init__(self, data: float):
        self.data = data


class NodeBase(object):
    """
    Data-agnostic base class for linked list nodes
    """

    __slots__ = ["data", "next_node"]

    def __init__(self, data):
        self.data = data
        self.next_node = None


class ListBase(object):
    """
    Data-agnostic base class for linked lists
    """

    __slots__ = ["size", "front_node"]

    def __init__(self):
        self.size = 0
        self.front_node = None

    def __iter__(self):
        lbi = ListBaseIterator(self)
        return lbi

    def length(self):
        return self.size


class ListBaseIterator(object):
    """
    Iterator object returned when iterating over a linked list
    """

    __slots__ = ["obj"]

    def __init__(self, obj):
        self.obj = obj

    def next(self):
        runner = self.obj.front_node
        while runner != None:
            yield runner.data
            runner = runner.next_node
        raise StopIteration()


class LocationNode(NodeBase):
    """
    Linked List Node for cell location (integer) data
    """

    __slots__ = ["data", "head", "next_node"]

    def __init__(self, data):
        self.data = data
        self.head = False
        self.next_node = None



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

    def to_list(self):
        r = []
        runner = self.back_node.next_node
        for i in range(self.size):
            r.append(runner.data)
            runner = runner.next_node
        return r

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


class LifeState(object):
    def __init__(
        self,
        rows: int,
        columns: int,
        rule_b: list,
        rule_s: list,
        neighbor_color_legacy_mode: bool = False,
    ):
        self.rows = rows
        self.columns = columns
        self.rule_b = rule_b
        self.rule_s = rule_s
        self.neighbor_color_legacy_mode = neighbor_color_legacy_mode
        self.statelist = LifeList(self.rows, self.columns)

    def is_alive(self, x, y):
        """Boolean: is the cell at (x, y) alive in this state?"""
        return self.statelist.contains(x, y)

    def count_live_cells(self):
        """Return count of live cells on the grid"""
        return self.statelist.ncellsongrid

    def add_cell(self, x, y):
        """Insert cell at (x, y) into state list"""
        return self.statelist.insert(x, y)

    def remove_cell(self, x, y):
        """
        Remove the given cell from the state
        """
        return self.statelist.remove(x, y)

    # def get_color_count(self, x, y):
    #    self.get_neighbor_count(x, y)

    # def get_neighbor_count(self, x, y):
    #    """Return a count of the number of neighbors of cell (x,y)"""
    #    neighbor_count = self.statelist.get_neighbor_count(x, y)
    #    return neighbor_count


class BinaryLifeState(LifeState):
    """
    A LifeState that combines two LifeStates for a binary game of life.
    This class provides a few additional methods.
    """

    def __init__(self, state1: LifeState, state2: LifeState):

        if state1.rows != state2.rows:
            err = "Error: CompositeLifeState received states of different sizes:\n"
            err += f"state 1 rows {state1.rows} != state 2 rows {state2.rows}"
            raise Exception(err)
        self.rows = state1.rows

        if state1.columns != state2.columns:
            err = "Error: CompositeLifeState received states of different sizes:\n"
            err += (
                f"state 1 columns {state1.columns} != state 2 columns {state2.columns}"
            )
            raise Exception(err)
        self.columns = state1.columns

        if not lists_equal(state1.rule_b, state2.rule_b):
            err = "Error: CompositeLifeState received states with different birth rules:\n"
            err += (
                f"state 1 rule b {state1.rule_b} != state 2 rule b {state2.rule_b}"
            )
            raise Exception(err)
        self.rule_b = state1.rule_b

        if not lists_equal(state1.rule_s, state2.rule_s):
            err = "Error: CompositeLifeState received states with different survival rules:\n"
            err += (
                f"state 1 rule b {state1.rule_s} != state 2 rule b {state2.rule_s}"
            )
            raise Exception(err)
        self.rule_s = state1.rule_s

        if state1.neighbor_color_legacy_mode != state2.neighbor_color_legacy_mode:
            err = "Error: CompositeLifeState received states with different neighbor_color_legacy_mode settings"
            raise Exception(err)
        self.neighbor_color_legacy_mode = state1.neighbor_color_legacy_mode

        self.statelist = LifeList(self.rows, self.columns)
        self.statelist1 = state1.statelist
        self.statelist2 = state2.statelist

    def is_alive(self, x, y):
        if self.statelist1.is_alive(x, y):
            return True
        elif self.statelist2.is_alive(x, y):
            return True
        return False

    def get_cell_color(self, x, y):
        if self.statelist1.is_alive(x, y):
            return 1
        elif self.statelist2.is_alive(x, y):
            return 2
        return 0

    def next_state(self):
        if self.statelist.size == 0:
            return

        (
            dead_neighbors,
            color1_dead_neighbors,
            color2_dead_neighbors,
            alive_neighbors,
            color1_neighbors,
            color2_neighbors,
        ) = self.statelist.get_all_neighbor_counts(
            self.statelist1, self.statelist2, self.neighbor_color_legacy_mode
        )

        # Process cells currently alive
        self.statelist.alive_to_dead(
            alive_neighbors,
            color1_neighbors,
            color2_neighbors,
            self.statelist1,
            self.statelist2,
            self.rule_b,
            self.rule_s,
            self.neighbor_color_legacy_mode,
        )

        # Process cells being born
        self.statelist.dead_to_alive(
            dead_neighbors,
            color1_dead_neighbors,
            color2_dead_neighbors,
            self.statelist1,
            self.statelist2,
            self.rule_b,
            self.rule_s,
            self.neighbor_color_legacy_mode,
        )


class LifeStats(object):
    """
    Object to hold statistical information about a Life object.
    This abstraction is messy, since the Life object creates LifeStats,
    but LifeStats still requires up-to-date information about the Life object,
    and changes the Life object when a victor is found.
    """
    livecells = 0
    livecells1 = 0
    livecells2 = 0
    victory = 0.0
    who_won = 0
    coverage = 0.0
    territory1 = 0.0
    territory2 = 0.0

    found_victor: bool = False

    running_avg_window: MovingAvgList
    running_avg_last3: MovingAvgList

    def __init__(self, life):
        self.running_avg_window = [
            0.0,
        ] * MAXDIM
        self.life = life
        self.rows = life.rows
        self.columns = life.columns
        self.running_avg_window = MovingAvgList()
        self.running_avg_last3 = MovingAvgList()
        self.found_victor = False

    def get_live_counts(self, state, state1, state2, generation):

        livecells = self.livecells = state.count_live_cells()
        livecells1 = self.livecells1 = state1.count_live_cells()
        livecells2 = self.livecells2 = state2.count_live_cells()

        victory = 0.0
        if livecells1 > livecells2:
            victory = (livecells1 / (1.0 * livecells1 + livecells2 + SMOL)) * 100
        else:
            victory = (livecells2 / (1.0 * livecells1 + livecells2 + SMOL)) * 100
        self.victory = victory
        total_area = self.columns * self.rows

        coverage = self.coverage = (livecells / (1.0 * total_area)) * 100
        territory1 = self.territory1 = (livecells1 / (1.0 * total_area)) * 100
        territory2 = self.territory2 = (livecells2 / (1.0 * total_area)) * 100

        try:
            last3list = self.running_avg_last3.to_list()
        except AttributeError:
            last3list = [0, 0, 0]

        return dict(
            generation=generation,
            liveCells=livecells,
            liveCells1=livecells1,
            liveCells2=livecells2,
            victoryPct=victory,
            coverage=coverage,
            territory1=territory1,
            territory2=territory2,
            last3=last3list,
        )

    def update_moving_avg(self):
        if not self.found_victor:
            if self.life.generation < MAXDIM:
                self.running_avg_window.push_back(self.victory)
            else:
                # pop front push back
                self.running_avg_window.push_back_pop_front(self.victory)
                running_avg = self.running_avg_window.avg()

                if self.running_avg_last3.length() < 3:
                    self.running_avg_last3.push_back(running_avg)
                    removed = 0
                else:
                    removed = self.running_avg_last3.push_back_pop_front(running_avg)

                tol = EQUALTOL
                # Skip the first few steps where we're removing zeros
                if not approx_equal(removed, 0.0, tol):
                    b1 = approx_equal(
                        self.running_avg_last3.index(0), self.running_avg_last3.index(1), tol
                    )
                    b2 = approx_equal(
                        self.running_avg_last3.index(1), self.running_avg_last3.index(2), tol
                    )
                    zerocells = self.livecells1 == 0 or self.livecells2 == 0
                    if (b1 and b2) or zerocells:
                        z1 = approx_equal(self.running_avg_last3.index(0), 50.0, tol)
                        z2 = approx_equal(self.running_avg_last3.index(1), 50.0, tol)
                        z3 = approx_equal(self.running_avg_last3.index(2), 50.0, tol)
                        if (not (z1 or z2 or z3)) or zerocells:
                            # Declare victory in the life object
                            if self.livecells1 > self.livecells2:
                                self.found_victor = True
                                self.who_won = 1
                            elif self.livecells1 < self.livecells2:
                                self.found_victor = True
                                self.who_won = 2


class OldSortedRowList(ListBase):
    """
    Linked List storing one row in a game of life.

    Schema for storage is to store the y coordinate as the first element,
    and sorted x locations as the following elements.

    [ y  x1  x2  x3  ... ]

    where x1, x2, x3 are in sorted order. Example:

    [ 100 15 16 19 ]

    represents the three cells (15,100) (16,100) (19,100)
    """

    __slots__ = ["rows", "columns", "size", "cellsongrid", "front_node"] ###, "back_node"]

    def __init__(self, rows, columns, x, y=None):
        self.rows = rows
        self.columns = columns

        self.size = 0
        self.cellsongrid = 0

        self.front_node = None
        ###self.back_node = None

        if y is not None:
            self.insert(y)
            self.insert(x)
        else:
            # x is actually y...
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

    def listify(self):
        r = []
        runner = self.front_node
        while runner != None:
            r.append(runner.data)
            runner = runner.next_node
        return r

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
        """
        Insert the given x location into the sorted list.
        Returns true if the insert succeeded.
        """

        if self.size == 0:
            # Handle empty list case first:
            # Create new Node and set it as the front and the back
            # (note x is actually y in this case)
            ynode = LocationNode(x)
            ynode.head = True
            self.front_node = ynode
            ###self.back_node = ynode
            self.size += 1
            # Do not increment cellsongrid, this is not an (x,y) point yet
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
                ###self.back_node = middle
            else:
                front.next_node = middle
                middle.next_node = back

            self.size += 1
            if self.head() >= 0 and self.head() < self.rows:
                if x >= 0 and x < self.columns:
                    self.cellsongrid += 1

            return True

    def insert_many_sorted(self, many_x):
        """
        Insert multiple values of x. The values MUST be in ascending sorted order!
        Returns number of inserts, and number of inserts on the grid.
        """
        assert self.size > 0
        runner = self.front_node
        ninserts = 0
        ninsertsongrid = 0
        for x in many_x:
            # Advance runner
            while runner.next_node is not None and (
                x > runner.next_node.data and runner.next_node.head is False
            ):
                runner = runner.next_node
            # Check this x value is not in the list already
            if (runner.next_node is None) or not (
                runner.next_node.data == x and runner.next_node.head is False
            ):
                # Insert node
                front = runner
                middle = LocationNode(x)
                back = runner.next_node
                front.next_node = middle
                middle.next_node = back
                ninserts += 1
                if self.head() >= 0 and self.head() < self.rows:
                    if x >= 0 and x < self.columns:
                        ninsertsongrid += 1
        self.size += ninserts
        self.cellsongrid += ninsertsongrid
        return ninserts, ninsertsongrid

    def remove(self, x):
        """
        Remove the given x location into the sorted list.
        """
        if self.size == 0 or self.size == 1:
            return False

        ii = self.insertion_index(x)
        if (ii.next_node is not None) and (ii.next_node.data == x):
            # Found it
            front = ii
            back = ii.next_node.next_node
            ### if back is None:
            ###     # The noded we are removing is the back of the list, update back pointer
            ###     self.back_node = front
            front.next_node = back
            self.size -= 1
            if self.head() >= 0 and self.head() < self.rows:
                if x >= 0 and x < self.columns:
                    self.cellsongrid -= 1
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


class SortedRowList(OldSortedRowList):
    __slots__ = [
        "rows",
        "columns",
        "size",
        "cellsongrid",
        "front_node",
        ###"back_node",
        "points_map",
    ]

    def __init__(self, *args, **kwargs):
        self.points_map = dict()
        super().__init__(*args, **kwargs)

    def insertion_index(self, x):
        """
        Given an element x, return a pointer to the insertion index
        (the Node preceding the spot where the new Node would go).
        If x is in the list, this returns the Node preceding it.
        This should only return None if the list is empty.
        The first element of the SortedRowList is y, so preceding Node
        should never be None.
        """
        if self.size == 0:
            return None

        elif self.size == 1:
            return self.front_node

        else:

            if x in self.points_map:
                ii = self.points_map[x]
                if ii is None:
                    # This should never happen
                    raise Exception(f"Error: could not find insertion index for {x}")
                else:
                    return ii
            else:
                leader = self.front_node.next_node
                lagger = self.front_node
                while leader != None and x > leader.data:
                    lagger = leader
                    leader = leader.next_node
                return lagger

    def insert(self, x):
        if self.size == 0:
            # Handle empty list case first:
            # Create new Node and set it as the front and the back
            # (note x is actually y in this case)
            ynode = LocationNode(x)
            ynode.head = True
            self.front_node = ynode
            ###self.back_node = ynode
            self.size += 1
            # Do not increment cellsongrid, this is not an (x,y) point yet
            # Do not add this to points_map, this is a y value not an x value
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
                ###self.back_node = middle
            else:
                front.next_node = middle
                middle.next_node = back
                self.points_map[back.data] = middle

            self.size += 1
            if self.head() >= 0 and self.head() < self.rows:
                if x >= 0 and x < self.columns:
                    self.cellsongrid += 1

            self.points_map[x] = ii
            return True

    def find(self, x):
        """
        Given an element x, return a pointer to the Node for that element,
        or return None if the item is not in the list.
        (To get preceding node, use insertion_index)
        """
        if self.size == 0 or self.size == 1:
            return None

        if x in self.points_map:
            ii = self.points_map[x]
            if ii is None:
                # This should never happen
                raise Exception(f"Error: could not find insertion index for {x}")
            else:
                return ii.next_node
        else:
            return None

    def insert_many_sorted(self, many_x):
        """
        Insert multiple values of x. The values MUST be in ascending sorted order!
        Returns number of inserts, and number of inserts on the grid.
        """
        assert self.size > 0
        runner = self.front_node
        ninserts = 0
        ninsertsongrid = 0
        for x in many_x:
            # Advance runner
            while runner.next_node is not None and (
                x > runner.next_node.data and runner.next_node.head is False
            ):
                runner = runner.next_node
            # Check this x value is not in the list already
            if (runner.next_node is None) or not (
                runner.next_node.data == x and runner.next_node.head is False
            ):
                # Insert node
                front = runner
                middle = LocationNode(x)
                back = runner.next_node
                front.next_node = middle
                middle.next_node = back
                if back is not None:
                    back_x = back.data
                    self.points_map[back_x] = middle
                ninserts += 1
                if self.head() >= 0 and self.head() < self.rows:
                    if x >= 0 and x < self.columns:
                        ninsertsongrid += 1
                self.points_map[x] = runner
        self.size += ninserts
        self.cellsongrid += ninsertsongrid
        return ninserts, ninsertsongrid

    def remove(self, x):
        """
        Remove the given x location into the sorted list.
        """
        if self.size == 0 or self.size == 1:
            return False

        if not self.contains(x):
            return False

        # When we remove, we need to update the entry for the node
        # following the node being removed
        ii = self.points_map[x]
        if (ii.next_node is not None) and (ii.next_node.data == x):
            # Found it
            front = ii
            back = ii.next_node.next_node
            if back is None:
                # The noded we are removing is the back of the list, update back pointer
                ###self.back_node = front
                back_x = None
            else:
                # Need to update back x insertion index in self.points_map
                back_x = back.data
            front.next_node = back
            self.size -= 1
            if self.head() >= 0 and self.head() < self.rows:
                if x >= 0 and x < self.columns:
                    self.cellsongrid -= 1
            del self.points_map[x]
            if back_x is not None:
                self.points_map[back_x] = front
            return True
        else:
            # x is in points_map but is not in the list
            raise Exception()

class RowNode(NodeBase):
    __slots__ = ["data", "next_node"]

    def __init__(self, data):
        self.data = data
        self.next_node = None


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

    __slots__ = [
        "rows",
        "columns",
        "size",
        "ncells",
        "ncellsongrid",
        "front_node",
        ###"back_node",
        "points_map",
    ]

    # TODO:
    # We could make getting the node associated with (x, y) an O(1) operation
    # When we add a new Node to the list, and increment count,
    # store a reference to Node in a hash table under key (x, y)

    # TODO:
    # reference(x, y) returns a reference to the Node containing point x in row y
    # insertion_index(x, y) returns what is actually stored - the insertion index (the node preceding that node)
    # both could be O(1) operations

    def __init__(self, rows, columns):
        self.points_map = dict()

        self.rows = rows
        self.columns = columns

        self.size = 0
        self.ncells = 0
        self.ncellsongrid = 0

        self.front_node = None
        ###self.back_node = None

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

    def listify(self):
        r = []
        runner = self.front_node
        while runner != None:
            r.append(runner.data.listify())
            runner = runner.next_node
        return r

    def serialize(self):
        s = "["
        yrunner = self.front_node
        while yrunner != None:
            row = yrunner.data
            y = row.head()
            s += '{"' + str(y) + '":['
            xrunner = row.front_node.next_node
            xlist = []
            while xrunner != None:
                x = xrunner.data
                s += str(x)
                if xrunner.next_node != None:
                    s += ","
                xrunner = xrunner.next_node
            s += "]}"
            if yrunner.next_node != None:
                s += ","
            yrunner = yrunner.next_node
        s += "]"
        return s

    def length(self):
        return self.size

    def soft_replace_with(self, other_life_list):
        """
        Replace contents of this lifelist with contents of other_life_list.
        This is a soft replacement, meaning we're just shifting links around.
        """
        self.front_node = other_life_list.front_node
        ###self.back_node = other_life_list.back_node
        self.points_map = other_life_list.points_map

        self.size = other_life_list.size
        self.ncells = other_life_list.ncells
        self.ncellsongrid = other_life_list.ncellsongrid

        self.rows = other_life_list.rows
        self.columns = other_life_list.columns

    def copy_points(self, other_lifelist):
        """
        Copy every point in another LifeList into this LifeList.
        Return a boolean: were any points copied.
        This method could be more efficient, but right now we just wanna get something working.
        """
        if other_lifelist.size == 0:
            return False

        else:
            # There is already at least 1 element in the list.

            ninserts = 0
            ninsertsongrid = 0
            other_yrunner = other_lifelist.front_node
            while other_yrunner != None:
                row = other_yrunner.data
                y = row.head()
                other_xrunner = row.front_node.next_node
                while other_xrunner != None:
                    x = other_xrunner.data
                    # Note: ncells is take care of by insert()
                    if self.insert(x, y):
                        ninserts += 1
                    other_xrunner = other_xrunner.next_node
                other_yrunner = other_yrunner.next_node

            return ninserts > 0

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
        #
        # NOTE:
        #
        # We could do this in O(1)
        # if we had a manifest, a set of all
        # (x,y) pairs that have gone into
        # the list
        #
        if self.size == 0:
            return False
        if self.find(x, y):
            return True
        else:
            return False

    def insert(self, x, y):
        """Insert the given (x, y) location into the correct list location"""

        # TODO:
        # Update a points manifest here

        if self.size == 0:
            # Handle empty list case first:
            # Create new Node and set it as the front
            row = SortedRowList(self.rows, self.columns, x, y)
            self.front_node = RowNode(row)
            self.size += 1
            self.ncells += 1
            if y >= 0 and y < self.rows:
                if x >= 0 and x < self.columns:
                    self.ncellsongrid += 1
            return True

        elif (self.size >= 1) and (self.front_node.data.head() == y):
            # Handle this case explicitly, to avoid the need for a ghost leader node.
            # In this case, the insertion index would be the ghost node before the front_node.
            this_row = self.front_node
            # y already has a row, insert x into it
            if this_row.data.insert(x):
                self.ncells += 1
                if y >= 0 and y < self.rows:
                    if x >= 0 and x < self.columns:
                        self.ncellsongrid += 1
                return True
            else:
                return False

        else:
            # There is already at least one row in the list.
            ii = self.insertion_index(y)

            if ii is None:
                # y does not have a row yet
                # if insertion index is none, the new row goes at the beginning
                row = SortedRowList(self.rows, self.columns, x, y)
                newfront = RowNode(row)
                oldfront = self.front_node
                newfront.next_node = oldfront
                self.front_node = newfront
                self.size += 1
                self.ncells += 1
                if y >= 0 and y < self.rows:
                    if x >= 0 and x < self.columns:
                        self.ncellsongrid += 1

            elif (ii.next_node is not None) and (ii.next_node.data.head() == y):
                this_row = ii.next_node
                # y already has a row in this list, insert x into it
                if this_row.data.insert(x):
                    self.ncells += 1
                    if y >= 0 and y < self.rows:
                        if x >= 0 and x < self.columns:
                            self.ncellsongrid += 1
                    return True
                else:
                    return False

            else:
                # y does not have a row yet
                # insert y into the list after the insertion index node
                front = ii
                back = ii.next_node
                row = SortedRowList(self.rows, self.columns, x, y)
                middle = RowNode(row)
                front.next_node = middle
                middle.next_node = back
                self.size += 1
                self.ncells += 1
                if y >= 0 and y < self.rows:
                    if x >= 0 and x < self.columns:
                        self.ncellsongrid += 1
                return True

    def insert_many_sorted(self, y, many_x):
        """
        Insert multiple sorted x values into the rowlist corresponding to y
        (or insert a new rowlist if one does not exist)
        """
        yii = self.insertion_index(y)
        if yii is None and self.front_node.data.head() == y:
            ninserts, ninsertsongrid = self.front_node.data.insert_many_sorted(many_x)
            self.ncells += ninserts
            self.ncellsongrid += ninsertsongrid
        elif (yii.next_node is not None) and (yii.next_node.data.head() == y):
            # We found y in the list
            # Call insert_many on the existing list
            ninserts, ninsertsongrid = yii.next_node.data.insert_many_sorted(many_x)
            self.ncells += ninserts
            self.ncellsongrid += ninsertsongrid
        else:
            # We did not find y in the list
            # Create a new row list, insert x values, and insert into list
            row = SortedRowList(self.rows, self.columns, y)
            ninserts, ninsertsongrid = row.insert_many_sorted(many_x)
            front = yii
            middle = RowNode(row)
            back = yii.next_node
            front.next_node = middle
            middle.next_node = back
            self.ncells += ninserts
            self.ncellsongrid += ninsertsongrid
            self.size += 1

    def remove(self, x, y):
        if self.size == 0:
            return False

        yii = self.insertion_index(y)

        if yii is None:

            # y goes at front of list
            front = self.front_node

            if front.data.head() == y:
                # y value already has a row, the first one
                row = self.front_node.data
                # remove from first row
                remove_worked = row.remove(x)
                if remove_worked:
                    self.ncells -= 1
                    if y >= 0 and y < self.rows:
                        if x >= 0 and x < self.columns:
                            self.ncellsongrid -= 1
                    # check if last x coordinate, if so remove this front row and replace front node pointer
                    if row.emptyx():
                        self.front_node = self.front_node.next_node
                        self.size -= 1
                return remove_worked

            else:
                # y value does not exist in list
                return False

        elif (yii.next_node is not None) and (yii.next_node.data.head() == y):

            # Found it in the list
            rowlist = yii.next_node.data
            remove_worked = rowlist.remove(x)
            if remove_worked:
                self.ncells -= 1
                if y >= 0 and y < self.rows:
                    if x >= 0 and x < self.columns:
                        self.ncellsongrid -= 1
                if rowlist.emptyx():
                    # This was the last x value in the row, so remove this row from listlife
                    front = yii
                    back = yii.next_node.next_node
                    front.next_node = back
                    self.size -= 1
            return remove_worked

        else:
            # y is not in the list
            return False

    def get_all_neighbor_counts(
        self,
        color1_lifelist,
        color2_lifelist,
        neighbor_color_legacy_mode=False,
    ):
        """
        Iterate over the entire grid and accumulate the following info:
        - count number of times dead neighbors are next to live cells
        - count number of live neighbors of live cells
        - count number of live (color 1) neighbors of live cells
        - count number of live (color 2) neighbors of live cells
        """
        # TODO:
        # Make this method more efficient.
        # Use of a reference(x, y) method that returns a Node pointer
        # would be very optimal, for making this method simpler.

        dead_neighbors = DeadNeighborCounter()
        color1_dead_neighbors = DeadNeighborCounter()
        color2_dead_neighbors = DeadNeighborCounter()
        alive_neighbors = AliveNeighborCounter()
        color1_neighbors = AliveNeighborCounter()
        color2_neighbors = AliveNeighborCounter()

        if self.size == 0:
            return dead_neighbors

        stencily_lag = None
        stencily_middle = self.front_node
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

                # Look up which color this cell is
                if color1_lifelist.contains(x, y):
                    xycolor = 1
                elif color2_lifelist.contains(x, y):
                    xycolor = 2
                else:
                    raise Exception()

                # -----------------------------------
                # Deal with above (lead) row
                if stencily_lead is None or stencily_lead.data.head() != y + 1:
                    # Row for y+1 is missing
                    # Add (x-1, y+1), (x, y+1), (x+1, y+1) to deadneighborcounter
                    dead_neighbors.accumulate(x - 1, y + 1)
                    dead_neighbors.accumulate(x, y + 1)
                    dead_neighbors.accumulate(x + 1, y + 1)
                    if xycolor == 1:
                        color1_dead_neighbors.accumulate(x - 1, y + 1)
                        color1_dead_neighbors.accumulate(x, y + 1)
                        color1_dead_neighbors.accumulate(x + 1, y + 1)
                    elif xycolor == 2:
                        color2_dead_neighbors.accumulate(x - 1, y + 1)
                        color2_dead_neighbors.accumulate(x, y + 1)
                        color2_dead_neighbors.accumulate(x + 1, y + 1)
                    else:
                        raise Exception()
                else:
                    # Scan lead row
                    aboverow = stencily_lead.data
                    abovexii = aboverow.insertion_index(x)

                    # Check for cell (x-1, y+1) in the list
                    if (abovexii.data == (x - 1)) and (abovexii.head is False):
                        # Found it
                        alive_neighbors.accumulate(x, y)
                        # Accumulate color counts for this cell using the neighbor's color
                        if color1_lifelist.contains(x - 1, y + 1):
                            xm1yp1color = 1
                        elif color2_lifelist.contains(x - 1, y + 1):
                            xm1yp1color = 2
                        else:
                            raise Exception(
                                f"Error: color at (x-1, y+1) = {x-1}, {y+1} is unknown"
                            )
                        if xm1yp1color == 1:
                            color1_neighbors.accumulate(x, y)
                        elif xm1yp1color == 2:
                            color2_neighbors.accumulate(x, y)
                        else:
                            raise Exception()
                    else:
                        # Not found
                        dead_neighbors.accumulate(x - 1, y + 1)
                        # Accumulate color counts for dead neighbor cell using our color
                        if xycolor == 1:
                            color1_dead_neighbors.accumulate(x - 1, y + 1)
                        elif xycolor == 2:
                            color2_dead_neighbors.accumulate(x - 1, y + 1)
                        else:
                            raise Exception()

                    # Check for cell (x, y+1)
                    # if x insertion index is at end of list, we are done with row
                    if abovexii.next_node is not None:

                        # Only advance insertion index if we find x
                        if (abovexii.next_node.data == x) and (
                            abovexii.next_node.head is False
                        ):
                            # Found it
                            alive_neighbors.accumulate(x, y)
                            # Accumulate color counts for this cell using the neighbor's color
                            if color1_lifelist.contains(x, y + 1):
                                xyp1color = 1
                            elif color2_lifelist.contains(x, y + 1):
                                xyp1color = 2
                            else:
                                raise Exception(
                                    f"Error: color at (x, y+1) = {x}, {y+1} is unknown"
                                )
                            if xyp1color == 1:
                                color1_neighbors.accumulate(x, y)
                            elif xyp1color == 2:
                                color2_neighbors.accumulate(x, y)
                            else:
                                raise Exception()
                            # Advance insertion index by 1
                            abovexii = abovexii.next_node
                        else:
                            # Not found
                            dead_neighbors.accumulate(x, y + 1)
                            # Accumulate color counts for dead neighbor cell using our color
                            if xycolor == 1:
                                color1_dead_neighbors.accumulate(x, y + 1)
                            elif xycolor == 2:
                                color2_dead_neighbors.accumulate(x, y + 1)
                            else:
                                raise Exception()

                        # Check for cell (x+1, y+1)
                        # If x+1 insertion index is at end of list, we are done with row
                        if abovexii.next_node is not None:

                            # Only advance insertion index if we find x+1
                            if (abovexii.next_node.data == (x + 1)) and (
                                abovexii.next_node.head is False
                            ):
                                # Found it
                                alive_neighbors.accumulate(x, y)
                                # Accumulate color counts for this cell using neighbor's color
                                if color1_lifelist.contains(x + 1, y + 1):
                                    xp1yp1color = 1
                                elif color2_lifelist.contains(x + 1, y + 1):
                                    xp1yp1color = 2
                                else:
                                    raise Exception(
                                        f"Error: color at (x+1, y+1) = {x+1}, {y+1} is unknown"
                                    )
                                if xp1yp1color == 1:
                                    color1_neighbors.accumulate(x, y)
                                elif xp1yp1color == 2:
                                    color2_neighbors.accumulate(x, y)
                                # No need to advance insertion index, done with this row
                            else:
                                # Cell (x+1, y+1) not found
                                dead_neighbors.accumulate(x + 1, y + 1)
                                # Accumulate color counts for dead neighbor cell using our color
                                if xycolor == 1:
                                    color1_dead_neighbors.accumulate(x + 1, y + 1)
                                elif xycolor == 2:
                                    color2_dead_neighbors.accumulate(x + 1, y + 1)
                                else:
                                    raise Exception()

                        else:
                            # Cell (x+1, y+1) not found
                            dead_neighbors.accumulate(x + 1, y + 1)
                            # Accumulate color counts for dead neighbor cell using our color
                            if xycolor == 1:
                                color1_dead_neighbors.accumulate(x + 1, y + 1)
                            elif xycolor == 2:
                                color2_dead_neighbors.accumulate(x + 1, y + 1)
                            else:
                                raise Exception()
                    else:
                        # Cell (x, y+1) not found
                        dead_neighbors.accumulate(x, y + 1)
                        dead_neighbors.accumulate(x + 1, y + 1)
                        # Accumulate color counts for dead neighbor cell using our color
                        if xycolor == 1:
                            color1_dead_neighbors.accumulate(x, y + 1)
                            color1_dead_neighbors.accumulate(x + 1, y + 1)
                        elif xycolor == 2:
                            color2_dead_neighbors.accumulate(x, y + 1)
                            color2_dead_neighbors.accumulate(x + 1, y + 1)
                        else:
                            raise Exception()

                # -----------------------------------
                # Deal with below (lag) row
                if stencily_lag is None or stencily_lag.data.head() != y - 1:
                    # Row for y-1 is missing
                    # Add cells (x-1, y-1), (x, y-1), (x+1, y-1) to deadneighborcounter
                    dead_neighbors.accumulate(x - 1, y - 1)
                    dead_neighbors.accumulate(x, y - 1)
                    dead_neighbors.accumulate(x + 1, y - 1)
                    if xycolor == 1:
                        color1_dead_neighbors.accumulate(x - 1, y - 1)
                        color1_dead_neighbors.accumulate(x, y - 1)
                        color1_dead_neighbors.accumulate(x + 1, y - 1)
                    elif xycolor == 2:
                        color2_dead_neighbors.accumulate(x - 1, y - 1)
                        color2_dead_neighbors.accumulate(x, y - 1)
                        color2_dead_neighbors.accumulate(x + 1, y - 1)
                    else:
                        raise Exception()
                else:
                    # Scan lag row
                    belowrow = stencily_lag.data
                    belowxii = belowrow.insertion_index(x)

                    # Check for cell (x-1, y-1) in the list
                    if (belowxii.data == (x - 1)) and (belowxii.head is False):
                        # Found it
                        alive_neighbors.accumulate(x, y)
                        # Accumulate color counts for this cell using the neighbor's color
                        if color1_lifelist.contains(x - 1, y - 1):
                            xm1ym1color = 1
                        elif color2_lifelist.contains(x - 1, y - 1):
                            xm1ym1color = 2
                        else:
                            raise Exception(
                                f"Error: color at (x-1, y-1) = {x-1}, {y-1} is unknown"
                            )
                        if xm1ym1color == 1:
                            color1_neighbors.accumulate(x, y)
                        elif xm1ym1color == 2:
                            color2_neighbors.accumulate(x, y)
                        else:
                            raise Exception()
                    else:
                        # Not found
                        dead_neighbors.accumulate(x - 1, y - 1)
                        # Accumulate color counts for dead neighbor cell using our color
                        if xycolor == 1:
                            color1_dead_neighbors.accumulate(x - 1, y - 1)
                        elif xycolor == 2:
                            color2_dead_neighbors.accumulate(x - 1, y - 1)
                        else:
                            raise Exception()

                    # Check for cell (x, y-1)
                    # if x insertion index is at end of list, we are done with row
                    if belowxii.next_node is not None:

                        if (belowxii.next_node.data == x) and (
                            belowxii.next_node.head is False
                        ):
                            # Found it
                            alive_neighbors.accumulate(x, y)
                            # Accumulate color counts for this cell using the neighbor's color
                            if color1_lifelist.contains(x, y - 1):
                                xym1color = 1
                            elif color2_lifelist.contains(x, y - 1):
                                xym1color = 2
                            else:
                                raise Exception(
                                    f"Error: color at (x, y-1) = {x}, {y-1} is unknown"
                                )
                            if xym1color == 1:
                                color1_neighbors.accumulate(x, y)
                            elif xym1color == 2:
                                color2_neighbors.accumulate(x, y)
                            else:
                                raise Exception()
                            # Advance insertion index by 1
                            belowxii = belowxii.next_node
                        else:
                            # Not found
                            dead_neighbors.accumulate(x, y - 1)
                            # Accumulate color counts for dead neighbor cell using our color
                            if xycolor == 1:
                                color1_dead_neighbors.accumulate(x, y - 1)
                            elif xycolor == 2:
                                color2_dead_neighbors.accumulate(x, y - 1)

                        # Check for cell (x+1, y-1)
                        # If x+1 insertion index is at end of list, we are done with row
                        if belowxii.next_node is not None:

                            # Only advance insertion index if we find x+1
                            if (belowxii.next_node.data == (x + 1)) and (
                                belowxii.next_node.head is False
                            ):
                                # Found it
                                alive_neighbors.accumulate(x, y)
                                # Accumulate color counts for this cell using neighbor's color
                                if color1_lifelist.contains(x + 1, y - 1):
                                    xp1ym1color = 1
                                elif color2_lifelist.contains(x + 1, y - 1):
                                    xp1ym1color = 2
                                else:
                                    raise Exception(
                                        f"Error: color at (x+1, y-1) = {x+1}, {y-1} is unknown"
                                    )
                                if xp1ym1color == 1:
                                    color1_neighbors.accumulate(x, y)
                                elif xp1ym1color == 2:
                                    color2_neighbors.accumulate(x, y)
                                else:
                                    raise Exception()

                            else:
                                # Cell (x+1, y-1) not found
                                dead_neighbors.accumulate(x + 1, y - 1)
                                # Accumulate color counts for dead neighbor cell using our color
                                if xycolor == 1:
                                    color1_dead_neighbors.accumulate(x + 1, y - 1)
                                elif xycolor == 2:
                                    color2_dead_neighbors.accumulate(x + 1, y - 1)
                                else:
                                    raise Exception()
                                # No need to advance insertion index, done with this row
                        else:
                            # Cell (x+1, y-1) not found
                            dead_neighbors.accumulate(x + 1, y - 1)
                            if xycolor == 1:
                                color1_dead_neighbors.accumulate(x + 1, y - 1)
                            elif xycolor == 2:
                                color2_dead_neighbors.accumulate(x + 1, y - 1)
                            else:
                                raise Exception()
                    else:
                        # Cell (x, y-1) not found
                        dead_neighbors.accumulate(x, y - 1)
                        dead_neighbors.accumulate(x + 1, y - 1)
                        # Accumulate color counts for dead neighbor cell using our color
                        if xycolor == 1:
                            color1_dead_neighbors.accumulate(x, y - 1)
                            color1_dead_neighbors.accumulate(x + 1, y - 1)
                        elif xycolor == 2:
                            color2_dead_neighbors.accumulate(x, y - 1)
                            color2_dead_neighbors.accumulate(x + 1, y - 1)
                        else:
                            raise Exception()

                # -----------------------------------
                # Deal with this row

                # Deal with cell (x-1, y)
                if (stencilx_lag.data == (x - 1)) and (stencilx_lag.head is False):
                    # Found it
                    alive_neighbors.accumulate(x, y)
                    # Accumulate color counts for this cell using the neighbor's color
                    if color1_lifelist.contains(x - 1, y):
                        xm1ycolor = 1
                    elif color2_lifelist.contains(x - 1, y):
                        xm1ycolor = 2
                    else:
                        raise Exception(
                            f"Error: color at (x+1, y) = {x+1}, {y} is unknown"
                        )
                    if xm1ycolor == 1:
                        color1_neighbors.accumulate(x, y)
                    elif xm1ycolor == 2:
                        color2_neighbors.accumulate(x, y)
                    else:
                        raise Exception()
                else:
                    # Not found
                    dead_neighbors.accumulate(x - 1, y)
                    if xycolor == 1:
                        color1_dead_neighbors.accumulate(x - 1, y)
                    elif xycolor == 2:
                        color2_dead_neighbors.accumulate(x - 1, y)
                    else:
                        raise Exception()

                # Deal with cell (x+1, y)
                if stencilx_lead is None or stencilx_lead.data != (x + 1):
                    # We do not have cell (x+1, y) i this list
                    dead_neighbors.accumulate(x + 1, y)
                    if xycolor == 1:
                        color1_dead_neighbors.accumulate(x + 1, y)
                    elif xycolor == 2:
                        color2_dead_neighbors.accumulate(x + 1, y)
                    else:
                        raise Exception()
                else:
                    # Not found
                    alive_neighbors.accumulate(x, y)
                    if color1_lifelist.contains(x + 1, y):
                        xp1ycolor = 1
                    elif color2_lifelist.contains(x + 1, y):
                        xp1ycolor = 2
                    else:
                        raise Exception(
                            f"    Error: color at (x+1, y) = {x+1}, {y} is unknown"
                        )
                    if xp1ycolor == 1:
                        color1_neighbors.accumulate(x, y)
                    elif xp1ycolor == 2:
                        color2_neighbors.accumulate(x, y)
                    else:
                        raise Exception()

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
                stencily_lead = stencily_lead.next_node

        return (
            dead_neighbors,
            color1_dead_neighbors,
            color2_dead_neighbors,
            alive_neighbors,
            color1_neighbors,
            color2_neighbors,
        )

    def alive_to_dead(
        self,
        alive_neighbors,
        color1_neighbors,
        color2_neighbors,
        s1,
        s2,
        rule_b,
        rule_s,
        neighbor_color_legacy_mode=False,
    ):
        """
        Iterate over every living cell, and kill cells with too many/too few neighbors.
        This must be called before dead_to_alive!!
        """
        if self.size == 0:
            return

        # Alive neighbors only stay alive if they have 2 or 3 alive neighbors
        alive_neighbors.filter_values(rule_s)

        # If cells are dead we remove them from self
        # If cells are still alive we add them to new state 1 or 2
        new_s1 = LifeList(self.rows, self.columns)
        new_s2 = LifeList(self.rows, self.columns)

        yrunner = self.front_node
        while yrunner is not None:
            y = yrunner.data.head()
            row = yrunner.data
            xrunner = row.front_node.next_node
            while xrunner is not None:
                x = xrunner.data
                c = alive_neighbors.count(x, y)
                if c not in rule_s:
                    # Remove point from binary life and color life
                    self.remove(x, y)
                    s1.remove(x, y)
                    s2.remove(x, y)

                else:
                    # Cell is already in self, now we just need to add it to the correct color lifelist
                    # Check color neighbor counts
                    c1 = color1_neighbors.count(x, y)
                    c2 = color2_neighbors.count(x, y)

                    # TODO:
                    # These inserts could be more efficient by keeping track
                    # of the last location inserted into...
                    if c1 > c2:
                        new_s1.insert(x, y)
                    elif c2 > c1:
                        new_s2.insert(x, y)
                    else:

                        if neighbor_color_legacy_mode:
                            new_s1.insert(x, y)
                        elif x % 2 == y % 2:
                            new_s1.insert(x, y)
                        else:
                            new_s2.insert(x, y)

                xrunner = xrunner.next_node
            yrunner = yrunner.next_node

        s1.soft_replace_with(new_s1)
        s2.soft_replace_with(new_s2)

    def dead_to_alive(
        self,
        dead_neighbors,
        color1_dead_neighbors,
        color2_dead_neighbors,
        s1,
        s2,
        rule_b,
        rule_s,
        neighbor_color_legacy_mode=False,
    ):
        """
        Use dead neighbor cell count to make dead cells alive
        """
        if self.size == 0:
            return

        # Dead neighbors only come alive if they have exactly 3 alive neighbors
        dead_neighbors.filter_values(rule_b)

        # Then, iterate over dead neighbor counts
        # Insert new cells into binary state
        # Then check their color and insert them into the correct new state

        for y in dead_neighbors.sorted_values():

            # Insert the new cell into the binary list life
            yii = self.insertion_index(y)
            xvalues = dead_neighbors.sorted_xvalues(y)

            # This is the easy one - all the points go into the binary life list.
            if yii is None:

                # y goes at front of list
                front = self.front_node
                row = front.data

                if row.head() == y:
                    # y value already has a row: the first one
                    # Insert each x into the cell
                    # (insert into color1/color2 state list happens below)
                    ninserts, ninsertsongrid = row.insert_many_sorted(xvalues)
                    self.ncells += ninserts
                    self.ncellsongrid += ninsertsongrid

                else:
                    # y value needs a new row
                    newrow = SortedRowList(self.rows, self.columns, y)
                    ninserts, ninsertsongrid = newrow.insert_many_sorted(xvalues)
                    # insert in front of list
                    newfront = RowNode(newrow)
                    oldfront = self.front_node
                    newfront.next_node = oldfront
                    self.front_node = newfront
                    self.ncells += ninserts
                    self.ncellsongrid += ninsertsongrid
                    self.size += 1

            elif yii.next_node is None:

                # y goes at end of list
                front = yii
                newrow = SortedRowList(self.rows, self.columns, y)
                ninserts, ninsertsongrid = newrow.insert_many_sorted(xvalues)
                # insert after insertion index
                back = RowNode(newrow)
                front.next_node = back
                self.ncells += ninserts
                self.ncellsongrid += ninsertsongrid
                self.size += 1

            else:
                front = yii
                row = front.next_node.data
                if row.head() == y:
                    # y value already has a row
                    ninserts, ninsertsongrid = row.insert_many_sorted(xvalues)
                    self.ncells += ninserts
                    self.ncellsongrid += ninsertsongrid
                else:
                    # y value needs a new row
                    newrow = SortedRowList(self.rows, self.columns, y)
                    ninserts, ninsertsongrid = newrow.insert_many_sorted(xvalues)
                    # insert between insertion index and insertion index next
                    middle = RowNode(newrow)
                    back = front.next_node
                    front.next_node = middle
                    middle.next_node = back
                    self.ncells += ninserts
                    self.ncellsongrid += ninsertsongrid
                    self.size += 1

            # For each new cell being born, determine its color
            # from the majority of its parent colors
            for x in xvalues:

                c1 = color1_dead_neighbors.count(x, y)
                c2 = color2_dead_neighbors.count(x, y)

                if c1 > c2:
                    s1.insert(x, y)
                elif c2 > c1:
                    s2.insert(x, y)
                else:

                    if neighbor_color_legacy_mode:
                        s1.insert(x, y)
                    elif x % 2 == y % 2:
                        s1.insert(x, y)
                    else:
                        s2.insert(x, y)


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

    def filter_lohi(self, lo, hi):
        for x in list(self.mapp.keys()):
            if not (self.mapp[x] >= lo and self.mapp[x] <= hi):
                del self.mapp[x]

    def filter_values(self, bag):
        for x in list(self.mapp.keys()):
            if not (self.mapp[x] in bag):
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

    def filter_lohi(self, lo, hi):
        """Filter all counts in this XYCounterStore to values that are between lo and hi"""
        for y in list(self.mapp.keys()):
            self.mapp[y].filter_lohi(lo, hi)
            x_values = self.mapp[y].mapp
            if len(x_values) == 0:
                del self.mapp[y]

    def filter_values(self, bag):
        """Filter all counts in this XYCounterStore to values that are between lo and hi"""
        for y in list(self.mapp.keys()):
            self.mapp[y].filter_values(bag)
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


class HellmouthBinaryLife(object):
    """
    Class to manage the state of a binary game of life.
    """

    actual_state: BinaryLifeState
    actual_state1: LifeState
    actual_state2: LifeState

    generation = 0
    columns = 0
    rows = 0

    row_b: list = []
    row_s: list = []

    running: bool = False
    neighbor_color_legacy_mode: bool = False

    def __init__(
        self,
        ic1: dict,
        ic2: dict,
        rows: int,
        columns: int,
        rule_b: list,
        rule_s: list,
        halt: bool = True,
        neighbor_color_legacy_mode: bool = False,
    ):
        self.ic1 = ic1
        self.ic2 = ic2

        self.rows = rows
        self.columns = columns

        self.rule_b = rule_b
        self.rule_s = rule_s

        self.neighbor_color_legacy_mode = neighbor_color_legacy_mode

        # Whether to stop when a victor is detected
        self.halt = halt

        self.running = True
        self.generation = 0
        self.stats = LifeStats(self)

        self.actual_state1 = LifeState(rows, columns, self.rule_b, self.rule_s, neighbor_color_legacy_mode)
        self.actual_state2 = LifeState(rows, columns, self.rule_b, self.rule_s, neighbor_color_legacy_mode)
        self.actual_state = BinaryLifeState(self.actual_state1, self.actual_state2)

        self.prepare()

    def prepare(self):
        s1 = self.ic1
        s2 = self.ic2

        for s1row in s1:
            for y in s1row:
                yy = int(y)
                for xx in s1row[y]:
                    self.actual_state.add_cell(xx, yy)
                    self.actual_state1.add_cell(xx, yy)

        for s2row in s2:
            for y in s2row:
                yy = int(y)
                for xx in s2row[y]:
                    self.actual_state.add_cell(xx, yy)
                    self.actual_state2.add_cell(xx, yy)

        self.get_stats()
        self.stats.update_moving_avg()

    def next_step(self):
        """Advance the state of the simulator forward by one time step"""
        if self.running is False:
            return self.get_stats()
        elif self.halt and self.check_for_victor():
            self.running = False
            return self.get_stats()
        else:
            self.generation += 1
            live_counts = self._next_generation()
            # Method above will call stats.get_live_counts()
            self.stats.update_moving_avg()
            if self.check_for_victor():
                self.running = False
            return live_counts

    def check_for_victor(self):
        if self.stats.found_victor:
            return True
        else:
            return False

    def _next_generation(self):
        """
        Advance life to the next generation.
        This only updates the game of life state, next_step updates the live counts and victory percent.
        """
        self.actual_state.next_state()
        return self.get_stats()

    def get_stats(self):
        """
        Get live counts of cells of each color, and total.
        Compute statistics.
        """
        return self.stats.get_live_counts(
            self.actual_state, self.actual_state1, self.actual_state2, self.generation
        )



def test_moving_avg_list():
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


