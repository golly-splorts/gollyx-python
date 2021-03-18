from operator import indexOf


class LifeState(object):
    def __init__(self, rows, columns, neighbor_color_legacy_mode=False):
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
                    state = state[:i] + state[i + 1:]
                    return
                else:
                    j = indexOf(row, x)
                    state[i] = row[:j] + row[j + 1:]

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


class CompositeLifeState(LifeState):
    """
    LifeState that combines the LifeStates of multiple colors.
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


class Life(object):
    actual_state: CompositeLifeState
    actual_state1: LifeState
    actual_state2: LifeState
    generation = 0
    columns = 0
    rows = 0
    livecells = 0
    livecells1 = 0
    livecells2 = 0
    victory = 0.0
    coverage = 0.0
    territory1 = 0.0
    territory2 = 0.0
    running_avg_window: list = []
    running_avg_last3: list = [0.0, 0.0, 0.0]
    found_victor: bool = False
    running: bool = False
    neighbor_color_legacy_mode: bool = False
    MAXDIM = 240

    def __init__(
        self,
        ic1: dict,
        ic2: dict,
        rows: int,
        columns: int,
        halt: bool = True,
        neighbor_color_legacy_mode: bool = False,
    ):
        self.ic1 = ic1
        self.ic2 = ic2
        self.rows = rows
        self.columns = columns
        # Whether to stop when a victor is detected
        self.halt = halt
        self.found_victor = False
        self.neighbor_color_legacy_mode = neighbor_color_legacy_mode
        self.running = True
        self.generation = 0

        self.actual_state1 = LifeState(rows, columns, neighbor_color_legacy_mode)
        self.actual_state2 = LifeState(rows, columns, neighbor_color_legacy_mode)
        self.actual_state = CompositeLifeState(self.actual_state1, self.actual_state2)

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

        maxdim = self.MAXDIM
        # maxdim = max(2 * self.columns, 2 * self.rows)
        self.running_avg_window = [
            0,
        ] * maxdim

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    def update_moving_avg(self, livecounts):
        if not self.found_victor:
            maxdim = self.MAXDIM
            # maxdim = max(2 * self.columns, 2 * self.rows)
            if self.generation < maxdim:
                self.running_avg_window[self.generation] = livecounts["victoryPct"]
            else:
                self.running_avg_window = self.running_avg_window[1:] + [
                    livecounts["victoryPct"]
                ]
                summ = sum(self.running_avg_window)
                running_avg = summ / (1.0 * len(self.running_avg_window))

                # update running average last 3
                removed = self.running_avg_last3[0]
                self.running_avg_last3 = self.running_avg_last3[1:] + [running_avg]

                tol = 1e-8
                # skip the first few steps where we're removing zeros
                if not self.approx_equal(removed, 0.0, tol):
                    b1 = self.approx_equal(
                        self.running_avg_last3[0], self.running_avg_last3[1], tol
                    )
                    b2 = self.approx_equal(
                        self.running_avg_last3[1], self.running_avg_last3[2], tol
                    )
                    zerocells = (
                        livecounts["liveCells1"] == 0 or livecounts["liveCells2"] == 0
                    )
                    if (b1 and b2) or zerocells:
                        z1 = self.approx_equal(self.running_avg_last3[0], 50.0, tol)
                        z2 = self.approx_equal(self.running_avg_last3[1], 50.0, tol)
                        z3 = self.approx_equal(self.running_avg_last3[2], 50.0, tol)
                        if (not (z1 or z2 or z3)) or zerocells:
                            if livecounts["liveCells1"] > livecounts["liveCells2"]:
                                self.found_victor = True
                                self.who_won = 1
                            elif livecounts["liveCells1"] < livecounts["liveCells2"]:
                                self.found_victor = True
                                self.who_won = 2

    def approx_equal(self, a, b, tol):
        SMOL = 1e-12
        return (abs(b - a) / abs(a + SMOL)) < tol

    # def is_alive(self, x, y):
    #    """
    #    Boolean function: is the cell at x, y alive
    #    """
    #    return self.actual_state.is_alive(x, y)

    # def get_cell_color(self, x, y):
    #    """
    #    Get the color of the given cell (1 or 2)
    #    """
    #    if self.actual_state1.is_alive(x, y):
    #        return 1
    #    elif self.actual_state2.is_alive(x, y):
    #        return 2
    #    else:
    #        return 0

    # def remove_cell(self, x, y, state):
    #    """
    #    Remove the given cell from the state
    #    """
    #    for i, row in enumerate(state):
    #        if row[0] == y:
    #            if len(row) == 2:
    #                # Remove the entire row
    #                state = state[:i] + state[i + 1 :]
    #                return
    #            else:
    #                j = indexOf(row, x)
    #                state[i] = row[:j] + row[j + 1 :]

    # def add_cell(self, x, y, state):
    #    """
    #    State is a list of arrays, where the y-coordinate is the first element,
    #    and the rest of the elements are x-coordinates:
    #      [y1, x1, x2, x3, x4]
    #      [y2, x5, x6, x7, x8, x9]
    #      [y3, x10]
    #    """
    #    # Empty state case
    #    if len(state) == 0:
    #        return [[y, x]]

    #    # figure out where in the list to insert the new cell
    #    if y < state[0][0]:
    #        # y is smaller than any existing y,
    #        # so put this point at beginning
    #        return [[y, x]] + state

    #    elif y > state[-1][0]:
    #        # y is larger than any existing y,
    #        # so put this point at end
    #        return state + [[y, x]]

    #    else:
    #        # Adding to the middle
    #        new_state = []
    #        added = False
    #        for row in state:
    #            if (not added) and (row[0] == y):
    #                # This level already exists
    #                new_row = [y]
    #                for c in row[1:]:
    #                    if (not added) and (x < c):
    #                        new_row.append(x)
    #                        added = True
    #                    new_row.append(c)
    #                if not added:
    #                    new_row.append(x)
    #                    added = True
    #                new_state.append(new_row)
    #            elif (not added) and (y < row[0]):
    #                # State does not include this row,
    #                # so create a new row
    #                new_row = [y, x]
    #                new_state.append(new_row)
    #                added = True
    #                # Also append the existing row
    #                new_state.append(row)
    #            else:
    #                new_state.append(row)

    #        if added is False:
    #            raise Exception(f"Error adding cell ({x},{y}): new_state = {new_state}")

    #        return new_state

    # def get_neighbors_from_alive(self, x, y, i, state, possible_neighbors_list):
    #    neighbors = 0
    #    neighbors1 = 0
    #    neighbors2 = 0

    #    # 1 row above current cell
    #    if i >= 1:
    #        if state[i - 1][0] == (y - 1):
    #            for k in range(self.top_pointer, len(state[i - 1])):
    #                if state[i - 1][k] >= (x - 1):

    #                    # NW
    #                    if state[i - 1][k] == (x - 1):
    #                        possible_neighbors_list[0] = [-1, -1, -1]
    #                        self.top_pointer = k + 1
    #                        neighbors += 1
    #                        xx = state[i - 1][k]
    #                        yy = state[i - 1][0]
    #                        neighborcolor = self.get_cell_color(xx, yy)
    #                        if neighborcolor == 1:
    #                            neighbors1 += 1
    #                        elif neighborcolor == 2:
    #                            neighbors2 += 1

    #                    # N
    #                    if state[i - 1][k] == x:
    #                        possible_neighbors_list[1] = [-1, -1, -1]
    #                        self.top_pointer = k
    #                        neighbors += 1
    #                        xx = state[i - 1][k]
    #                        yy = state[i - 1][0]
    #                        neighborcolor = self.get_cell_color(xx, yy)
    #                        if neighborcolor == 1:
    #                            neighbors1 += 1
    #                        elif neighborcolor == 2:
    #                            neighbors2 += 1

    #                    # NE
    #                    if state[i - 1][k] == (x + 1):
    #                        possible_neighbors_list[2] = [-1, -1, -1]
    #                        if k == 1:
    #                            self.top_pointer = 1
    #                        else:
    #                            self.top_pointer = k - 1
    #                        neighbors += 1
    #                        xx = state[i - 1][k]
    #                        yy = state[i - 1][0]
    #                        neighborcolor = self.get_cell_color(xx, yy)
    #                        if neighborcolor == 1:
    #                            neighbors1 += 1
    #                        elif neighborcolor == 2:
    #                            neighbors2 += 1

    #                    # Break it off early
    #                    if state[i - 1][k] > (x + 1):
    #                        break

    #    # The row of the current cell
    #    for k in range(1, len(state[i])):
    #        if state[i][k] >= (x - 1):

    #            # W
    #            if state[i][k] == (x - 1):
    #                possible_neighbors_list[3] = [-1, -1, -1]
    #                neighbors += 1
    #                xx = state[i][k]
    #                yy = state[i][0]
    #                neighborcolor = self.get_cell_color(xx, yy)
    #                if neighborcolor == 1:
    #                    neighbors1 += 1
    #                elif neighborcolor == 2:
    #                    neighbors2 += 1

    #            # E
    #            if state[i][k] == (x + 1):
    #                possible_neighbors_list[4] = [-1, -1, -1]
    #                neighbors += 1
    #                xx = state[i][k]
    #                yy = state[i][0]
    #                neighborcolor = self.get_cell_color(xx, yy)
    #                if neighborcolor == 1:
    #                    neighbors1 += 1
    #                elif neighborcolor == 2:
    #                    neighbors2 += 1

    #            # Break it off early
    #            if state[i][k] > (x + 1):
    #                break

    #    # 1 row below current cell
    #    if i + 1 < len(state):
    #        if state[i + 1][0] == (y + 1):
    #            for k in range(self.bottom_pointer, len(state[i + 1])):
    #                if state[i + 1][k] >= (x - 1):

    #                    # SW
    #                    if state[i + 1][k] == (x - 1):
    #                        possible_neighbors_list[5] = [-1, -1, -1]
    #                        self.bottom_pointer = k + 1
    #                        neighbors += 1
    #                        xx = state[i + 1][k]
    #                        yy = state[i + 1][0]
    #                        neighborcolor = self.get_cell_color(xx, yy)
    #                        if neighborcolor == 1:
    #                            neighbors1 += 1
    #                        elif neighborcolor == 2:
    #                            neighbors2 += 1

    #                    # S
    #                    if state[i + 1][k] == x:
    #                        possible_neighbors_list[6] = [-1, -1, -1]
    #                        self.bottom_pointer = k
    #                        neighbors += 1
    #                        xx = state[i + 1][k]
    #                        yy = state[i + 1][0]
    #                        neighborcolor = self.get_cell_color(xx, yy)
    #                        if neighborcolor == 1:
    #                            neighbors1 += 1
    #                        elif neighborcolor == 2:
    #                            neighbors2 += 1

    #                    # SE
    #                    if state[i + 1][k] == (x + 1):
    #                        possible_neighbors_list[7] = [-1, -1, -1]
    #                        if k == 1:
    #                            self.bottom_pinter = 1
    #                        else:
    #                            self.bottom_pointer = k - 1
    #                        neighbors += 1
    #                        xx = state[i + 1][k]
    #                        yy = state[i + 1][0]
    #                        neighborcolor = self.get_cell_color(xx, yy)
    #                        if neighborcolor == 1:
    #                            neighbors1 += 1
    #                        elif neighborcolor == 2:
    #                            neighbors2 += 1

    #                    # Break it off early
    #                    if state[i + 1][k] > (x + 1):
    #                        break

    #    color = 0
    #    if neighbors1 > neighbors2:
    #        color = 1
    #    elif neighbors2 > neighbors1:
    #        color = 2
    #    else:
    #        if self.neighbor_color_legacy_mode:
    #            color = 1
    #        elif x % 2 == y % 2:
    #            color = 1
    #        else:
    #            color = 2

    #    return dict(neighbors=neighbors, color=color)

    def get_color_from_alive(self, x, y):
        """
        This function seems redundant, but is slightly different.
        The above function is for dead cells that become alive.
        This function is for dead cells that come alive because of THOSE cells.
        """
        color1 = self.actual_state1.get_color_count(x, y)
        color2 = self.actual_state2.get_color_count(x, y)

        if color1 > color2:
            return 1
        elif color1 < color2:
            return 2
        else:
            if self.neighbor_color_legacy_mode:
                color = 1
            elif x % 2 == y % 2:
                color = 1
            else:
                color = 2
            return color

    def next_generation(self):
        all_dead_neighbors = {}

        new_state1 = LifeState(self.rows, self.columns)
        new_state2 = LifeState(self.rows, self.columns)
        new_state = CompositeLifeState(new_state1, new_state2)

        self.redraw_list = []

        for i in range(len(self.actual_state.state)):
            self.actual_state.top_pointer = 1
            self.actual_state.bottom_pointer = 1

            for j in range(1, len(self.actual_state.state[i])):
                x = self.actual_state.state[i][j]
                y = self.actual_state.state[i][0]

                # create a list of possible dead neighbors
                # get_neighbors_from_alive() will pare this down
                dead_neighbors = [
                    [x - 1, y - 1, 1],
                    [x, y - 1, 1],
                    [x + 1, y - 1, 1],
                    [x - 1, y, 1],
                    [x + 1, y, 1],
                    [x - 1, y + 1, 1],
                    [x, y + 1, 1],
                    [x + 1, y + 1, 1],
                ]

                result = self.actual_state.get_neighbors_from_alive(
                    x, y, i, dead_neighbors
                )
                neighbors = result["neighbors"]
                color = result["color"]

                # join dead neighbors remaining to check list
                for dead_neighbor in dead_neighbors:
                    # if dead_neighbor is not None:
                    if dead_neighbor[2] != -1:
                        # this cell is dead
                        xx = dead_neighbor[0]
                        yy = dead_neighbor[1]
                        key = str(xx) + "," + str(yy)

                        # counting number of dead neighbors
                        if key not in all_dead_neighbors:
                            all_dead_neighbors[key] = 1
                        else:
                            all_dead_neighbors[key] += 1

                if neighbors < 0:
                    raise Exception(
                        f"Error: neighbors has invalid value of {neighbors}"
                    )
                elif not (neighbors == 0 or neighbors == 1 or neighbors > 3):
                    if color == 1:
                        new_state.add_cell(x, y)
                        new_state1.add_cell(x, y)
                    elif color == 2:
                        new_state.add_cell(x, y)
                        new_state2.add_cell(x, y)
                    self.redraw_list.append([x, y, 2])
                else:
                    # Kill cell
                    self.redraw_list.append([x, y, 0])

        # Process dead neighbors
        for key in all_dead_neighbors:
            if all_dead_neighbors[key] == 3:
                # This cell is dead, but has enough neighbors
                # that are alive that it will make new life
                key = key.split(",")
                t1 = int(key[0])
                t2 = int(key[1])

                # Get color from neighboring parent cells
                color = self.get_color_from_alive(t1, t2)

                if color == 1:
                    new_state.add_cell(t1, t2)
                    new_state1.add_cell(t1, t2)
                elif color == 2:
                    new_state.add_cell(t1, t2)
                    new_state2.add_cell(t1, t2)

                self.redraw_list.append([t1, t2, 1])

        self.actual_state = new_state
        self.actual_state1 = new_state1
        self.actual_state2 = new_state2

        return self.get_live_counts()

    # def next_generation(self):
    #    """
    #    Evolve the actual_state list life state to the next generation.
    #    """
    #    all_dead_neighbors = {}

    #    new_state = []
    #    new_state1 = []
    #    new_state2 = []

    #    self.redraw_list = []

    #    for i in range(len(self.actual_state)):
    #        self.top_pointer = 1
    #        self.bottom_pointer = 1

    #        for j in range(1, len(self.actual_state[i])):
    #            x = self.actual_state[i][j]
    #            y = self.actual_state[i][0]

    #            # create a list of possible dead neighbors
    #            # get_neighbors_from_alive() will pare this down
    #            dead_neighbors = [
    #                [x - 1, y - 1, 1],
    #                [x, y - 1, 1],
    #                [x + 1, y - 1, 1],
    #                [x - 1, y, 1],
    #                [x + 1, y, 1],
    #                [x - 1, y + 1, 1],
    #                [x, y + 1, 1],
    #                [x + 1, y + 1, 1],
    #            ]

    #            result = self.actual_state.get_neighbors_from_alive(
    #                x, y, i, dead_neighbors
    #            )
    #            neighbors = result["neighbors"]
    #            color = result["color"]

    #            # join dead neighbors remaining to check list
    #            for dead_neighbor in dead_neighbors:
    #                #if dead_neighbor is not None:
    #                if dead_neighbor[2] != -1:
    #                    # this cell is dead
    #                    xx = dead_neighbor[0]
    #                    yy = dead_neighbor[1]
    #                    key = str(xx) + "," + str(yy)

    #                    # counting number of dead neighbors
    #                    if key not in all_dead_neighbors:
    #                        all_dead_neighbors[key] = 1
    #                    else:
    #                        all_dead_neighbors[key] += 1

    #            if (neighbors < 0 ):
    #                raise Exception(f"Error: neighbors has invalid value of {neighbors}")
    #            elif not (neighbors == 0 or neighbors == 1 or neighbors > 3):
    #                new_state = self.add_cell(x, y, new_state)
    #                if color == 1:
    #                    new_state1 = self.add_cell(x, y, new_state1)
    #                elif color == 2:
    #                    new_state2 = self.add_cell(x, y, new_state2)
    #                # Keep cell alive
    #                self.redraw_list.append([x, y, 2])
    #            else:
    #                # Kill cell
    #                self.redraw_list.append([x, y, 0])

    #    # Process dead neighbors
    #    for key in all_dead_neighbors:
    #        if all_dead_neighbors[key] == 3:
    #            # This cell is dead, but has enough neighbors
    #            # that are alive that it will make new life
    #            key = key.split(",")
    #            t1 = int(key[0])
    #            t2 = int(key[1])

    #            # Get color from neighboring parent cells
    #            color = self.get_color_from_alive(t1, t2)

    #            new_state = self.add_cell(t1, t2, new_state)
    #            if color == 1:
    #                new_state1 = self.add_cell(t1, t2, new_state1)
    #            elif color == 2:
    #                new_state2 = self.add_cell(t1, t2, new_state2)

    #            self.redraw_list.append([t1, t2, 1])

    #    self.actual_state = new_state
    #    self.actual_state1 = new_state1
    #    self.actual_state2 = new_state2

    #    return self.get_live_counts()

    def get_live_counts(self):
        """
        Get live counts of cells of each color, and total.
        Compute statistics.
        """
        livecells = self.livecells = self.actual_state.count_live_cells()
        livecells1 = self.livecells1 = self.actual_state1.count_live_cells()
        livecells2 = self.livecells2 = self.actual_state2.count_live_cells()

        victory = 0.0
        SMOL = 1e-12
        if livecells1 > livecells2:
            victory = livecells1 / (1.0 * livecells1 + livecells2 + SMOL)
        else:
            victory = livecells2 / (1.0 * livecells1 + livecells2 + SMOL)
        victory = victory * 100
        self.victory = victory

        total_area = self.columns * self.rows
        coverage = livecells / (1.0 * total_area)
        coverage = coverage * 100
        self.coverage = coverage

        territory1 = self.territory1 = (livecells1 / (1.0 * total_area)) * 100
        territory2 = self.territory2 = (livecells2 / (1.0 * total_area)) * 100

        return dict(
            generation=self.generation,
            liveCells=livecells,
            liveCells1=livecells1,
            liveCells2=livecells2,
            victoryPct=victory,
            coverage=coverage,
            territory1=territory1,
            territory2=territory2,
        )

    def next_step(self):
        if self.running is False:
            return self.get_live_counts()
        elif self.halt and self.found_victor:
            self.running = False
            return self.get_live_counts()
        else:
            self.generation += 1
            live_counts = self.next_generation()
            self.update_moving_avg(live_counts)
            return live_counts
