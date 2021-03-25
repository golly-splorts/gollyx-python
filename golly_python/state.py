from operator import indexOf
from .linkedlists import LifeList


class LifeState(object):
    def __init__(
        self, rows: int, columns: int, neighbor_color_legacy_mode: bool = False
    ):
        self.statelist = LifeList()
        self.rows = rows
        self.columns = columns
        self.neighbor_color_legacy_mode = neighbor_color_legacy_mode

    def is_alive(self, x, y):
        """Boolean: is the cell at (x, y) alive in this state?"""
        return self.statelist.contains(x, y)

    def count_live_cells(self):
        """Return count of live cells"""
        return self.statelist.live_count()

    def add_cell(self, x, y):
        """Insert cell at (x, y) into state list"""
        return self.statelist.insert(x, y)

    def remove_cell(self, x, y):
        """
        Remove the given cell from the state
        """
        return self.statelist.remove(x, y)

    def get_color_count(self, x, y):
        self.get_neighbor_count(x, y)

    def get_neighbor_count(self, x, y):
        """Return a count of the number of neighbors of cell (x,y)"""
        neighbor_count = self.statelist.get_neighbor_count(x, y)
        return neighbor_count


class BinaryLifeState(LifeState):
    """
    A LifeState that combines two LifeStates for a binary game of life.
    This class provides a few additional methods.
    """

    def __init__(self, state1: LifeState, state2: LifeState):

        self.statelist = LifeList()

        if state1.rows != state2.rows:
            err = "Error: CompositeLifeState received states of different sizes:\n"
            err += f"state 1 rows {state1.rows} != state 2 rows {state2.rows}"
            raise Exception(err)
        self.rows = state1.rows

        if state1.columns != state2.columns:
            err = "Error: CompositeLifeState received states of different sizes:\n"
            err += f"state 1 columns {state1.columns} != state 2 columns {state2.columns}"
            raise Exception(err)
        self.columns = state1.columns

        self.statelist1 = state1.statelist
        self.statelist2 = state2.statelist

        if (
            state1.neighbor_color_legacy_mode
            != state2.neighbor_color_legacy_mode
        ):
            err = "Error: CompositeLifeState received states with different neighbor_color_legacy_mode settings"
            raise Exception(err)
        self.neighbor_color_legacy_mode = state1.neighbor_color_legacy_mode

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
        if self.statelist.size==0:
            return

        print(type(self.statelist1))

        (
            dead_neighbors,
            color1_dead_neighbors,
            color2_dead_neighbors,
            alive_neighbors,
            color1_neighbors,
            color2_neighbors,
        ) = self.statelist.get_all_neighbor_counts(self.statelist1, self.statelist2)

        # Process cells currently alive
        self.statelist.alive_to_dead(
            alive_neighbors,
            color1_neighbors,
            color2_neighbors,
            self.statelist1,
            self.statelist2,
        )

        # Process cells being born
        self.statelist.dead_to_alive(
            dead_neighbors,
            color1_dead_neighbors,
            color2_dead_neighbors,
            self.statelist1,
            self.statelist2,
            self.neighbor_color_legacy_mode
        )



### class OldLifeState(object):
###     def __init__(
###         self, rows: int, columns: int, neighbor_color_legacy_mode: bool = False
###     ):
###         self.state = []
###         self.rows = rows
###         self.columns = columns
###         self.neighbor_color_legacy_mode = neighbor_color_legacy_mode
### 
###     def is_alive(self, x, y):
###         """
###         Boolean function: is the cell at x, y alive
###         """
###         for row in self.state:
###             if row[0] == y:
###                 for c in row[1:]:
###                     if c == x:
###                         return True
###         return False
### 
###     def count_live_cells(self):
###         livecells = 0
###         for row in self.state:
###             if (row[0] >= 0) and (row[0] < self.rows):
###                 for j in range(1, len(row)):
###                     if (row[j] >= 0) and (row[j] < self.columns):
###                         livecells += 1
###         return livecells
### 
###     def add_cell(self, x, y):
###         """
###         State is a list of arrays, where the y-coordinate is the first element,
###         and the rest of the elements are x-coordinates:
###           [y1, x1, x2, x3, x4]
###           [y2, x5, x6, x7, x8, x9]
###           [y3, x10]
###         """
###         # Empty state case
###         if len(self.state) == 0:
###             self.state = [[y, x]]
###             return
### 
###         # figure out where in the list to insert the new cell
###         elif y < self.state[0][0]:
###             # y is smaller than any existing y,
###             # so put this point at beginning
###             self.state = [[y, x]] + self.state
###             return
### 
###         elif y > self.state[-1][0]:
###             # y is larger than any existing y,
###             # so put this point at end
###             self.state = self.state + [[y, x]]
###             return
### 
###         else:
###             # Adding to the middle
###             new_state = []
###             added = False
###             for row in self.state:
###                 if (not added) and (row[0] == y):
###                     # This level already exists
###                     new_row = [y]
###                     for c in row[1:]:
###                         if (not added) and (x < c):
###                             # Add the new cell in the middle
###                             new_row.append(x)
###                             added = True
###                         # Add all the other cells as usual
###                         new_row.append(c)
###                     if not added:
###                         # Add the new cell to the end
###                         new_row.append(x)
###                         added = True
###                     new_state.append(new_row)
###                 elif (not added) and (y < row[0]):
###                     # State does not include this row,
###                     # so create a new row
###                     new_row = [y, x]
###                     new_state.append(new_row)
###                     added = True
###                     # Also append the existing row
###                     new_state.append(row)
###                 else:
###                     new_state.append(row)
### 
###             if added is False:
###                 raise Exception(f"Error adding cell ({x},{y}): new_state = {new_state}")
### 
###             self.state = new_state
###             return
### 
###     def remove_cell(self, x, y):
###         """
###         Remove the given cell from the state
###         """
###         state = self.state
###         for i, row in enumerate(state):
###             if row[0] == y:
###                 if len(row) == 2:
###                     # Remove the entire row
###                     state = state[:i] + state[i + 1 :]
###                     return
###                 else:
###                     j = indexOf(row, x)
###                     state[i] = row[:j] + row[j + 1 :]
### 
###     def get_color_count(self, x, y):
###         """
###         This function determines the colors of dead cells becoming alive
###         """
###         state = self.state
###         color = 0
###         for i in range(len(state)):
###             yy = state[i][0]
###             if yy == (y - 1):
###                 # 1 row above current cell
###                 for j in range(1, len(state[i])):
###                     xx = state[i][j]
###                     if xx >= (x - 1):
###                         if xx == (x - 1):
###                             # NW
###                             color += 1
###                         elif xx == x:
###                             # N
###                             color += 1
###                         elif xx == (x + 1):
###                             # NE
###                             color += 1
###                     if xx >= (x + 1):
###                         break
### 
###             elif yy == y:
###                 # Row of current cell
###                 for j in range(1, len(state[i])):
###                     xx = state[i][j]
###                     if xx >= (x - 1):
###                         if xx == (x - 1):
###                             # W
###                             color += 1
###                         elif xx == (x + 1):
###                             # E
###                             color += 1
###                     if xx >= (x + 1):
###                         break
### 
###             elif yy == (y + 1):
###                 # 1 row below current cell
###                 for j in range(1, len(state[i])):
###                     xx = state[i][j]
###                     if xx >= (x - 1):
###                         if xx == (x - 1):
###                             # SW
###                             color += 1
###                         elif xx == x:
###                             # S
###                             color += 1
###                         elif xx == (x + 1):
###                             # SE
###                             color += 1
###                     if xx >= (x + 1):
###                         break
### 
###         return color
