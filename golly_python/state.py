from operator import indexOf


class LifeState(object):
    def __init__(
        self, rows: int, columns: int, neighbor_color_legacy_mode: bool = False
    ):
        self.state = LifeList()
        self.rows = rows
        self.columns = columns
        self.neighbor_color_legacy_mode = neighbor_color_legacy_mode

    def is_alive(self, x, y):
        """Boolean: is the cell at (x, y) alive in this state?"""
        return self.state.contains(x, y)

    def count_live_cells(self):
        """Return count of live cells"""
        return self.state.live_count()

    def add_cell(self, x, y):
        """Insert cell at (x, y) into state list"""
        return self.state.insert(x, y)

    def remove_cell(self, x, y):
        """
        Remove the given cell from the state
        """
        return self.state.remove(x, y)













class OldLifeState(object):
    def __init__(
        self, rows: int, columns: int, neighbor_color_legacy_mode: bool = False
    ):
        self.state = []
        self.rows = rows
        self.columns = columns
        self.neighbor_color_legacy_mode = neighbor_color_legacy_mode

    def is_alive(self, x, y):
        """
        Boolean function: is the cell at x, y alive
        """
        for row in self.state:
            if row[0] == y:
                for c in row[1:]:
                    if c == x:
                        return True
        return False

    def count_live_cells(self):
        livecells = 0
        for row in self.state:
            if (row[0] >= 0) and (row[0] < self.rows):
                for j in range(1, len(row)):
                    if (row[j] >= 0) and (row[j] < self.columns):
                        livecells += 1
        return livecells

    def add_cell(self, x, y):
        """
        State is a list of arrays, where the y-coordinate is the first element,
        and the rest of the elements are x-coordinates:
          [y1, x1, x2, x3, x4]
          [y2, x5, x6, x7, x8, x9]
          [y3, x10]
        """
        # Empty state case
        if len(self.state) == 0:
            self.state = [[y, x]]
            return

        # figure out where in the list to insert the new cell
        elif y < self.state[0][0]:
            # y is smaller than any existing y,
            # so put this point at beginning
            self.state = [[y, x]] + self.state
            return

        elif y > self.state[-1][0]:
            # y is larger than any existing y,
            # so put this point at end
            self.state = self.state + [[y, x]]
            return

        else:
            # Adding to the middle
            new_state = []
            added = False
            for row in self.state:
                if (not added) and (row[0] == y):
                    # This level already exists
                    new_row = [y]
                    for c in row[1:]:
                        if (not added) and (x < c):
                            # Add the new cell in the middle
                            new_row.append(x)
                            added = True
                        # Add all the other cells as usual
                        new_row.append(c)
                    if not added:
                        # Add the new cell to the end
                        new_row.append(x)
                        added = True
                    new_state.append(new_row)
                elif (not added) and (y < row[0]):
                    # State does not include this row,
                    # so create a new row
                    new_row = [y, x]
                    new_state.append(new_row)
                    added = True
                    # Also append the existing row
                    new_state.append(row)
                else:
                    new_state.append(row)

            if added is False:
                raise Exception(f"Error adding cell ({x},{y}): new_state = {new_state}")

            self.state = new_state
            return

    def remove_cell(self, x, y):
        """
        Remove the given cell from the state
        """
        state = self.state
        for i, row in enumerate(state):
            if row[0] == y:
                if len(row) == 2:
                    # Remove the entire row
                    state = state[:i] + state[i + 1 :]
                    return
                else:
                    j = indexOf(row, x)
                    state[i] = row[:j] + row[j + 1 :]

    def get_color_count(self, x, y):
        """
        This function determines the colors of dead cells becoming alive
        """
        state = self.state
        color = 0
        for i in range(len(state)):
            yy = state[i][0]
            if yy == (y - 1):
                # 1 row above current cell
                for j in range(1, len(state[i])):
                    xx = state[i][j]
                    if xx >= (x - 1):
                        if xx == (x - 1):
                            # NW
                            color += 1
                        elif xx == x:
                            # N
                            color += 1
                        elif xx == (x + 1):
                            # NE
                            color += 1
                    if xx >= (x + 1):
                        break

            elif yy == y:
                # Row of current cell
                for j in range(1, len(state[i])):
                    xx = state[i][j]
                    if xx >= (x - 1):
                        if xx == (x - 1):
                            # W
                            color += 1
                        elif xx == (x + 1):
                            # E
                            color += 1
                    if xx >= (x + 1):
                        break

            elif yy == (y + 1):
                # 1 row below current cell
                for j in range(1, len(state[i])):
                    xx = state[i][j]
                    if xx >= (x - 1):
                        if xx == (x - 1):
                            # SW
                            color += 1
                        elif xx == x:
                            # S
                            color += 1
                        elif xx == (x + 1):
                            # SE
                            color += 1
                    if xx >= (x + 1):
                        break

        return color


class BinaryLifeState(LifeState):
    """
    A LifeState that combines two LifeStates for a binary game of life.
    This class provides a few additional methods.
    """

    def __init__(self, state1: LifeState, state2: LifeState):
        self.state = []
        self.state1 = state1
        self.state2 = state2

        if self.state1.rows != self.state2.rows:
            err = "Error: CompositeLifeState received states of different sizes:\n"
            err += f"state 1 rows {self.state1.rows} != state 2 rows {self.state2.rows}"
            raise Exception(err)
        self.rows = self.state1.rows

        if self.state1.columns != self.state2.columns:
            err = "Error: CompositeLifeState received states of different sizes:\n"
            err += f"state 1 columns {self.state1.columns} != state 2 columns {self.state2.columns}"
            raise Exception(err)
        self.columns = self.state1.columns

        if (
            self.state1.neighbor_color_legacy_mode
            != self.state2.neighbor_color_legacy_mode
        ):
            err = "Error: CompositeLifeState received states with different neighbor_color_legacy_mode settings"
            raise Exception(err)
        self.neighbor_color_legacy_mode = self.state1.neighbor_color_legacy_mode

    def is_alive(self, x, y):
        if self.state1.is_alive(x, y):
            return True
        elif self.state2.is_alive(x, y):
            return True
        return False

    def get_cell_color(self, x, y):
        if self.state1.is_alive(x, y):
            return 1
        elif self.state2.is_alive(x, y):
            return 2
        return 0

    def get_neighbors_from_alive(self, x, y, i, possible_neighbors_list):
        state = self.state

        neighbors = 0
        neighbors1 = 0
        neighbors2 = 0

        # 1 row above current cell
        if i >= 1:
            if state[i - 1][0] == (y - 1):
                for k in range(self.top_pointer, len(state[i - 1])):
                    if state[i - 1][k] >= (x - 1):

                        # NW
                        if state[i - 1][k] == (x - 1):
                            possible_neighbors_list[0] = [-1, -1, -1]
                            self.top_pointer = k + 1
                            neighbors += 1
                            xx = state[i - 1][k]
                            yy = state[i - 1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # N
                        if state[i - 1][k] == x:
                            possible_neighbors_list[1] = [-1, -1, -1]
                            self.top_pointer = k
                            neighbors += 1
                            xx = state[i - 1][k]
                            yy = state[i - 1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # NE
                        if state[i - 1][k] == (x + 1):
                            possible_neighbors_list[2] = [-1, -1, -1]
                            if k == 1:
                                self.top_pointer = 1
                            else:
                                self.top_pointer = k - 1
                            neighbors += 1
                            xx = state[i - 1][k]
                            yy = state[i - 1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # Break it off early
                        if state[i - 1][k] > (x + 1):
                            break

        # The row of the current cell
        for k in range(1, len(state[i])):
            if state[i][k] >= (x - 1):

                # W
                if state[i][k] == (x - 1):
                    possible_neighbors_list[3] = [-1, -1, -1]
                    neighbors += 1
                    xx = state[i][k]
                    yy = state[i][0]
                    neighborcolor = self.get_cell_color(xx, yy)
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1

                # E
                if state[i][k] == (x + 1):
                    possible_neighbors_list[4] = [-1, -1, -1]
                    neighbors += 1
                    xx = state[i][k]
                    yy = state[i][0]
                    neighborcolor = self.get_cell_color(xx, yy)
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1

                # Break it off early
                if state[i][k] > (x + 1):
                    break

        # 1 row below current cell
        if i + 1 < len(state):
            if state[i + 1][0] == (y + 1):
                for k in range(self.bottom_pointer, len(state[i + 1])):
                    if state[i + 1][k] >= (x - 1):

                        # SW
                        if state[i + 1][k] == (x - 1):
                            possible_neighbors_list[5] = [-1, -1, -1]
                            self.bottom_pointer = k + 1
                            neighbors += 1
                            xx = state[i + 1][k]
                            yy = state[i + 1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # S
                        if state[i + 1][k] == x:
                            possible_neighbors_list[6] = [-1, -1, -1]
                            self.bottom_pointer = k
                            neighbors += 1
                            xx = state[i + 1][k]
                            yy = state[i + 1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # SE
                        if state[i + 1][k] == (x + 1):
                            possible_neighbors_list[7] = [-1, -1, -1]
                            if k == 1:
                                self.bottom_pinter = 1
                            else:
                                self.bottom_pointer = k - 1
                            neighbors += 1
                            xx = state[i + 1][k]
                            yy = state[i + 1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # Break it off early
                        if state[i + 1][k] > (x + 1):
                            break

        color = 0
        if neighbors1 > neighbors2:
            color = 1
        elif neighbors2 > neighbors1:
            color = 2
        else:
            if self.neighbor_color_legacy_mode:
                color = 1
            elif x % 2 == y % 2:
                color = 1
            else:
                color = 2

        return dict(neighbors=neighbors, color=color)
