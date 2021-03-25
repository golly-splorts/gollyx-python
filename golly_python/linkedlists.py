class XCounterStore(object):
    """
    Small utilty class used by XYCounterStore
    to store counters for a set of x values.
    Wraps a hash map of x values to integer counts.
    """

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


class NodeBase(object):
    """
    Data-agnostic base class for linked list nodes
    """

    data = None
    next_node = None

    def __init__(self, data):
        self.data = data


class ListBase(object):
    """
    Data-agnostic base class for linked lists
    """

    size: int = 0
    front_node: NodeBase = None

    def __init__(self):
        pass

    def __iter__(self):
        lbi = ListBaseIterator(self)
        return lbi

    def length(self):
        return self.size


class ListBaseIterator(object):
    """
    Iterator object returned when iterating over a linked list
    """

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

    data: int = 0
    head: bool = False


class SortedRowList(object):
    """
    Linked List storing one row in a game of life.

    Schema for storage is to store the y coordinate as the first element,
    and sorted x locations as the following elements.

    [ y  x1  x2  x3  ... ]

    where x1, x2, x3 are in sorted order. Example:

    [ 100 15 16 19 ]

    represents the three cells (15,100) (16,100) (19,100)
    """

    size: int = 0
    front_node: LocationNode = None
    back_node: LocationNode = None

    # TODO:
    # Optimally, some of these insert methods would return the node,
    # so that inserts don't always have to start at the beginning.

    # TODO:
    # contains() would be faster if we had a hash table of points

    def __init__(self, x, y=None):
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
            # (note x is actually y in this case)
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

    def insert_many_sorted(self, many_x):
        """
        Insert multiple values of x. The values MUST be in ascending sorted order!
        """
        assert self.size > 0
        runner = self.front_node
        ninserts = 0
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
        return ninserts

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

    # TODO:
    # This class will be a lot faster if it keeps a hash table of points it contains

    # TODO:
    # We could make getting the node associated with (x, y) an O(1) operation
    # When we add a new Node to the list, and increment count,
    # store a reference to Node in a hash table under key (x, y)

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

    def soft_replace_with(self, other_life_list):
        """
        Replace contents of this lifelist with contents of other_life_list.
        This is a soft replacement, meaning we're just shifting links around.
        """
        self.front_node = other_life_list.front_node
        self.size = other_life_list.size
        self.ncells = other_life_list.ncells

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

            ### # TODO:
            ### # Use two yrunners, handling cases where they are empty
            ### this_yrunner = self.front_node
            ### other_yrunner = other_lifelist.front_node

            ### while other_yrunner is not None:
            ###     this_y = this_yrunner.data.head()
            ###     other_y = other_yrunner.data.head()
            ###     while other_y > this_y and this_yrunner is not None:
            ###         this_yrunner = this_yrunner.next_node

            ninserts = 0
            other_yrunner = other_lifelist.front_node
            while other_yrunner != None:
                row = other_yrunner.data
                y = row.head()
                other_xrunner = row.front_node.next_node
                while other_xrunner != None:
                    x = other_xrunner.data
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
        # if we had a ledger (set of all
        # (x,y) pairs that have gone into
        # the list)
        #
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

    def insert_many_sorted(self, y, many_x):
        yii = self.insertion_index(y)
        if yii is None and self.front_node.data.head() == y:
            ninserts = self.front_node.data.insert_many_sorted(many_x)
            self.ncells += ninserts
        elif (yii.next_node is not None) and (yii.next_node.data.head() == y):
            # We found y in the list
            # Call insert_many on the existing list
            ninserts = yii.next_node.data.insert_many_sorted(many_x)
            self.ncells += ninserts
        else:
            # We did not find y in the list
            # Create a new row list, insert x values, and insert into list
            row = SortedRowList(y)
            ninserts = row.insert_many_sorted(many_x)
            front = yii
            middle = RowNode(row)
            back = yii.next_node
            front.next_node = middle
            middle.next_node = back
            self.ncells += ninserts
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
                    # check if last x coordinate, if so remove this list
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
        - based on color counts of live cells, insert into color1_lifelist or color2_lifelist
        """
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
                        if xm1yp1color == 1:
                            color1_neighbors.accumulate(x, y)
                        elif xm1yp1color == 2:
                            color2_neighbors.accumulate(x, y)
                    else:
                        # Not found
                        dead_neighbors.accumulate(x - 1, y + 1)
                        # Accumulate color counts for dead neighbor cell using our color
                        if xycolor == 1:
                            color1_dead_neighbors.accumulate(x - 1, y + 1)
                        elif xycolor == 2:
                            color2_dead_neighbors.accumulate(x - 1, y + 1)

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
                            if xyp1color == 1:
                                color1_neighbors.accumulate(x, y)
                            elif xyp1color == 2:
                                color2_neighbors.accumulate(x, y)
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
                            # Cell (x+1, y+1) not found
                            dead_neighbors.accumulate(x + 1, y + 1)
                            # Accumulate color counts for dead neighbor cell using our color
                            if xycolor == 1:
                                color1_dead_neighbors.accumulate(x + 1, y + 1)
                            elif xycolor == 2:
                                color2_dead_neighbors.accumulate(x + 1, y + 1)
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
                        if xm1ym1color == 1:
                            color1_neighbors.accumulate(x, y)
                        elif xm1ym1color == 2:
                            color2_neighbors.accumulate(x, y)
                    else:
                        # Not found
                        dead_neighbors.accumulate(x - 1, y - 1)
                        # Accumulate color counts for dead neighbor cell using our color
                        if xycolor == 1:
                            color1_dead_neighbors.accumulate(x - 1, y - 1)
                        elif xycolor == 2:
                            color2_dead_neighbors.accumulate(x - 1, y - 1)

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
                            if xym1color == 1:
                                color1_neighbors.accumulate(x, y)
                            elif xym1color == 2:
                                color2_neighbors.accumulate(x, y)
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
                                if xp1ym1color == 1:
                                    color1_neighbors.accumulate(x, y)
                                elif xp1ym1color == 2:
                                    color2_neighbors.accumulate(x, y)

                            else:
                                # Cell (x+1, y-1) not found
                                dead_neighbors.accumulate(x + 1, y - 1)
                                # Accumulate color counts for dead neighbor cell using our color
                                if xycolor == 1:
                                    color1_dead_neighbors.accumulate(x + 1, y - 1)
                                elif xycolor == 2:
                                    color2_dead_neighbors.accumulate(x + 1, y - 1)
                                # No need to advance insertion index, done with this row
                        else:
                            # Cell (x+1, y-1) not found
                            dead_neighbors.accumulate(x + 1, y - 1)
                            if xycolor == 1:
                                color1_dead_neighbors.accumulate(x + 1, y - 1)
                            elif xycolor == 2:
                                color2_dead_neighbors.accumulate(x + 1, y - 1)
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
                    if xm1ycolor == 1:
                        color1_neighbors.accumulate(x, y)
                    elif xm1ycolor == 2:
                        color2_neighbors.accumulate(x, y)
                else:
                    # Not found
                    dead_neighbors.accumulate(x - 1, y)
                    if xycolor == 1:
                        color1_dead_neighbors.accumulate(x - 1, y)
                    elif xycolor == 2:
                        color2_dead_neighbors.accumulate(x - 1, y)

                # Deal with cell (x+1, y)
                if stencilx_lead is None or stencilx_lead.data != (x + 1):
                    # We do not have cell (x+1, y) i this list
                    dead_neighbors.accumulate(x + 1, y)
                    if xycolor == 1:
                        color1_dead_neighbors.accumulate(x + 1, y)
                    elif xycolor == 2:
                        color2_dead_neighbors.accumulate(x + 1, y)
                else:
                    # Not found
                    alive_neighbors.accumulate(x, y)
                    if color1_lifelist.contains(x + 1, y):
                        xp1ycolor = 1
                    elif color2_lifelist.contains(x + 1, y):
                        xp1ycolor = 2
                    if xp1ycolor == 1:
                        color1_neighbors.accumulate(x, y)
                    elif xp1ycolor == 2:
                        color2_neighbors.accumulate(x, y)

                ### # Deal with cell (x, y) last
                ### # (we require live neighbor counts to know
                ### # which state to add (x, y) to)
                ### if (stencilx_middle.data == x) and (stencilx_middle.head is False):
                ###     alive_neighbors.accumulate(x, y)

                ###     c1 = color1_neighbors.count(x, y)
                ###     c2 = color2_neighbors.count(x, y)

                ###     if c1 > c2:
                ###         print(f"updating point {x}, {y} to state 1")
                ###         print(f"  c1 = {c1}, c2 = {c2}")
                ###         color1_lifelist.insert(x, y)
                ###     elif c2 > c1:
                ###         print(f"updating point {x}, {y} to state 2")
                ###         print(f"  c1 = {c1}, c2 = {c2}")
                ###         color2_lifelist.insert(x, y)
                ###     else:

                ###         if neighbor_color_legacy_mode:
                ###             print(f"updating point {x}, {y} to state 1")
                ###             print(f"  c1 = {c1}, c2 = {c2}")
                ###             color1_lifelist.insert(x, y)
                ###         elif x % 2 == y % 2:
                ###             print(f"updating point {x}, {y} to state 1")
                ###             print(f"  c1 = {c1}, c2 = {c2}")
                ###             color1_lifelist.insert(x, y)
                ###         else:
                ###             print(f"updating point {x}, {y} to state 2")
                ###             print(f"  c1 = {c1}, c2 = {c2}")
                ###             color2_lifelist.insert(x, y)

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
        neighbor_color_legacy_mode=False,
    ):
        """
        Iterate over every living cell, and kill cells with too many/too few neighbors.
        This must be called before dead_to_alive!!
        """
        if self.size == 0:
            return

        # Alive neighbors only stay alive if they have 2 or 3 alive neighbors
        alive_neighbors.filter(2, 3)

        # If cells are dead we remove them from self
        # If cells are still alive we add them to new state 1 or 2
        new_s1 = LifeList()
        new_s2 = LifeList()

        yrunner = self.front_node
        while yrunner is not None:
            y = yrunner.data.head()
            row = yrunner.data
            xrunner = row.front_node.next_node
            while xrunner is not None:
                x = xrunner.data
                c = alive_neighbors.count(x, y)
                if c != 2 and c != 3:
                    # Remove point from binary life and color life
                    self.remove(x, y)

                else:
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
        neighbor_color_legacy_mode=False,
    ):
        """
        Use dead neighbor cell count to make dead cells alive
        """
        if self.size == 0:
            return

        # Dead neighbors only come alive if they have exactly 3 alive neighbors
        dead_neighbors.filter(3, 3)

        # Then, iterate over dead neighbor counts
        # Insert new cells into binary state
        # Then check their color and insert them into the correct new state

        yvalues = dead_neighbors.mapp
        for y in list(yvalues.keys()):

            # Insert the new cell into the binary list life
            yii = self.insertion_index(y)
            xvalues = list(dead_neighbors.mapp[y].mapp.keys())

            # This is the easy one - all the points go into the binary life list.
            if yii is None:

                # y goes at front of list
                front = self.front_node

                if front.data.head() == y:
                    # y value already has a row: the first one
                    row = self.front_node.data

                    # Insert each x into the cell
                    # (insert into color1/color2 state list happens below)
                    ninserts = row.insert_many_sorted(xvalues)
                    self.ncells += ninserts

                else:
                    # y value needs a new row
                    ninserts = row.insert_many_sorted(xvalues)
                    middle = RowNode(newrow)
                    back = front.next_node
                    newrow = SortedRowList(y)
                    front.next_node = middle
                    middle.next_node = back
                    self.ncells += ninserts
                    self.size += 1

            elif yii.next_node is None:
                # Next y value goes at end of list
                newrow = SortedRowList(y)
                ninserts = newrow.insert_many_sorted(xvalues)
                back = RowNode(newrow)
                front.next_node = back
                self.ncells += ninserts
                self.nsize += 1

            else:
                front = yii.next_node
                row = front.data
                if row.head() == y:
                    # y value already has a row
                    ninserts = row.insert_many_sorted(xvalues)
                    self.ncells += ninserts
                else:
                    # y value needs a new row
                    newrow = SortedRowList(y)
                    ninserts = newrows.insert_many_sorted(xvalues)
                    middle = RowNode(neworw)
                    middle.next_node = back
                    front.next_node = middle
                    self.ncells += ninserts
                    self.nsize += 1

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

    #print("="*40)

    #print("Before get all neighbor counts:")
    #print(binary)
    #print("before get all neighbor counts s1:")
    #print(s1)
    #print("before get all neighbor counts s2:")
    #print(s2)

    (
        dead_neighbors,
        color1_dead_neighbors,
        color2_dead_neighbors,
        alive_neighbors,
        color1_neighbors,
        color2_neighbors,
    ) = binary.get_all_neighbor_counts(s1, s2)

    #print("After get all neighbor counts:")
    #print(binary)
    #print("after get all neighbor counts s1:")
    #print(s1)
    #print("after get all neighbor counts s2:")
    #print(s2)

    print("="*40)

    print("Before alive to dead:")
    print(binary)
    print("before alive to dead s1:")
    print(s1)
    print("before alive to dead s2:")
    print(s2)

    binary.alive_to_dead(
        alive_neighbors, 
        color1_neighbors, 
        color2_neighbors, 
        s1, 
        s2
    )

    print("After alive to dead:")
    print(binary)
    print("After alive to dead s1:")
    print(s1)
    print("After alive to dead s2:")
    print(s2)

    print("="*40)

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
