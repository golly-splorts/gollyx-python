from operator import indexOf
import json
import math


class KleinBinaryLife(object):

    actual_state: list = []
    actual_state1: list = []
    actual_state2: list = []
    running_avg_window: list = []
    running_avg_last3: list = []

    generation = 0
    columns = 0
    rows = 0

    row_b: list = []
    row_s: list = []

    livecells = 0
    livecells1 = 0
    livecells2 = 0

    victory = 0.0
    who_won = 0
    coverage = 0.0

    found_victor = False
    running_avg_window: list = []
    running_avg_last3: list = [0.0, 0.0, 0.0]
    running = False
    periodic = True

    found_victor: bool = False

    tol_zero = 1e-8
    tol_stable = 1e-8

    MAXDIM = 240

    def __init__(
        self,
        ic1: dict,
        ic2: dict,
        rows: int,
        columns: int,
        rule_b: list = [],
        rule_s: list = [],
        halt: bool = True,
        tol_zero: float = None,
        tol_stable: float = None,
    ):
        self.ic1 = ic1
        self.ic2 = ic2

        self.rows = rows
        self.columns = columns

        self.rule_b = rule_b
        self.rule_s = rule_s

        # Tolerances
        if tol_zero is not None:
            self.tol_zero = tol_zero
        if tol_stable is not None:
            self.tol_stable = tol_stable
        if self.tol_zero < 0 or self.tol_stable < 0:
            raise Exception(f"Error: tolerances must be > 0")

        self.actual_state = []
        self.actual_state1 = []
        self.actual_state2 = []

        # Whether to stop when a victor is detected
        self.halt = halt

        self.running = True
        self.generation = 0

        self.running_avg_window = [0,]*self.MAXDIM
        self.running_avg_last3 = [0, 0, 0]
        self.found_victor = False

        self.set_initial_state()

    def set_initial_state(self):
        s1 = self.ic1
        s2 = self.ic2

        for s1row in s1:
            for y in s1row:
                yy = int(y)
                for xx in s1row[y]:
                    self.actual_state = self.add_cell(xx, yy, self.actual_state)
                    self.actual_state1 = self.add_cell(xx, yy, self.actual_state1)

        for s2row in s2:
            for y in s2row:
                yy = int(y)
                for xx in s2row[y]:
                    self.actual_state = self.add_cell(xx, yy, self.actual_state)
                    self.actual_state2 = self.add_cell(xx, yy, self.actual_state2)

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    def check_for_victor(self):
        if self.found_victor:
            return True
        else:
            return False

    def update_moving_avg(self, livecounts):
        if livecounts is None:
            livecounts = self.get_live_counts()

        if not self.found_victor:
            maxdim = self.MAXDIM
            # maxdim = max(2 * self.columns, 2 * self.rows)

            rootsum = 0
            rootsum = math.sqrt(livecounts['liveCells1']**2 + livecounts['liveCells2']**2)

            if self.generation < maxdim:
                self.running_avg_window[self.generation] = rootsum
            else:
                self.running_avg_window = self.running_avg_window[1:] + [rootsum]
                summ = sum(self.running_avg_window)
                running_avg = summ / (1.0 * len(self.running_avg_window))

                # update running average last 3
                removed = self.running_avg_last3[0]
                self.running_avg_last3 = self.running_avg_last3[1:] + [running_avg]

                tol_zero = self.tol_zero
                tol_stable = self.tol_stable

                # skip the first few steps where we're removing zeros
                if not self.approx_equal(removed, 0.0, tol_zero):
                    # We are here because we have a nonzero running average (game is going), and no victor
                    # Check if average has become stable
                    b1 = self.approx_equal(
                        self.running_avg_last3[0], self.running_avg_last3[1], tol_stable
                    )
                    b2 = self.approx_equal(
                        self.running_avg_last3[1], self.running_avg_last3[2], tol_stable
                    )
                    victory_by_stability = (b1 and b2) and (livecounts['liveCells'] > 0)

                    if victory_by_stability:
                        # Someone won due to simulation becoming stable
                        self.found_victor = True
                        if livecounts["liveCellsColors"][0] > livecounts["liveCellsColors"][1]:
                            self.who_won = 1
                        elif livecounts["liveCellsColors"][0] < livecounts["liveCellsColors"][1]:
                            self.who_won = 2
                        else:
                            # Tie
                            self.who_won = -1

            # The second way for a victor to be declared,
            # is to have all other teams get shut out.
            # But if gen < maxDim, this game is invalid.
            victory_by_shutout = (livecounts['liveCells1']==0 or livecounts['liveCells2']==0)

            if victory_by_shutout:
                # Someone won by shutting out the other team
                self.found_victor = True
                if self.generation < maxdim:
                    self.who_won = -1
                else:
                    if livecounts["liveCells1"] > livecounts["liveCells2"]:
                        self.who_won = 1
                    elif livecounts["liveCells1"][0] < livecounts["liveCells2"]:
                        self.who_won = 2
                    else:
                        # Tie
                        self.who_won = -1

    def next_step(self):
        """
        basically a wrapper for next_generation method
        """
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

    def next_generation(self):
        """
        Evolve the actual_state list life state to the next generation.
        """
        all_dead_neighbors = {}

        new_state = []
        new_state1 = []
        new_state2 = []

        self.redraw_list = []

        for i in range(len(self.actual_state)):

            for j in range(1, len(self.actual_state[i])):
                x = self.actual_state[i][j]
                y = self.actual_state[i][0]

                xm1 = x - 1
                ym1 = y - 1

                xp1 = x + 1
                yp1 = y + 1

                if self.periodic:

                    xm1 = self.periodic_normalize_x(x - 1)
                    ym1 = self.periodic_normalize_y(y - 1)

                    xp1 = self.periodic_normalize_x(x + 1)
                    yp1 = self.periodic_normalize_y(y + 1)

                    x = self.periodic_normalize_x(x)
                    y = self.periodic_normalize_y(y)

                # create a list of possible dead neighbors
                # get_neighbors_from_alive() will pare this down
                dead_neighbors = [
                    [xm1, ym1, 1],
                    [x,   ym1, 1],
                    [xp1, ym1, 1],
                    [xm1, y,   1],
                    [xp1, y,   1],
                    [xm1, yp1, 1],
                    [x,   yp1, 1],
                    [xp1, yp1, 1],
                ]

                result = self.get_neighbors_from_alive(
                    x, y, i, self.actual_state, dead_neighbors
                )
                neighbors = result["neighbors"]
                color = result["color"]

                # join dead neighbors remaining to check list
                for dead_neighbor in dead_neighbors:
                    if dead_neighbor is not None:
                        # this cell is dead
                        xx = dead_neighbor[0]
                        yy = dead_neighbor[1]
                        key = str(xx) + "," + str(yy)

                        # counting number of dead neighbors
                        if key not in all_dead_neighbors:
                            all_dead_neighbors[key] = 1
                        else:
                            all_dead_neighbors[key] += 1

                if not (neighbors == 0 or neighbors == 1 or neighbors > 3):
                    new_state = self.add_cell(x, y, new_state)

                    if color == -1:
                        color = self.get_cell_color(x, y)

                    if color == 1:
                        new_state1 = self.add_cell(x, y, new_state1)
                    elif color == 2:
                        new_state2 = self.add_cell(x, y, new_state2)
                    # Keep cell alive
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

                new_state = self.add_cell(t1, t2, new_state)
                if color == 1:
                    new_state1 = self.add_cell(t1, t2, new_state1)
                elif color == 2:
                    new_state2 = self.add_cell(t1, t2, new_state2)

                self.redraw_list.append([t1, t2, 1])

        self.actual_state = new_state
        self.actual_state1 = new_state1
        self.actual_state2 = new_state2

        return self.get_live_counts()

    def get_live_counts(self):
        """
        Get live counts of cells of each color, and total.
        Compute statistics.
        """

        def _count_live_cells(state):
            livecells = 0
            for i in range(len(state)):
                if (state[i][0] >= 0) and (state[i][0] < self.rows):
                    for j in range(1, len(state[i])):
                        if (state[i][j] >= 0) and (state[i][j] < self.columns):
                            livecells += 1
            return livecells

        livecells = _count_live_cells(self.actual_state)
        livecells1 = _count_live_cells(self.actual_state1)
        livecells2 = _count_live_cells(self.actual_state2)

        self.livecells = livecells
        self.livecells1 = livecells1
        self.livecells2 = livecells2

        SMOL = 1e-12

        total_area = self.columns * self.rows
        coverage = livecells / (1.0 * total_area + SMOL)
        coverage = coverage * 100
        self.coverage = coverage

        return dict(
            generation=self.generation,
            liveCells=livecells,
            liveCells1=livecells1,
            liveCells2=livecells2,
            coverage=coverage,
        )

    def get_neighbors_from_alive(self, x, y, i, state, possible_neighbors_list):
        neighbors = 0
        neighbors1 = 0
        neighbors2 = 0

        xm1 = x - 1
        ym1 = y - 1

        xp1 = x + 1
        yp1 = y + 1

        periodic = self.periodic
        if periodic:
            x = self.periodic_normalize_x(x)
            y = self.periodic_normalize_y(y)

            xm1 = self.periodic_normalize_x(xm1)
            ym1 = self.periodic_normalize_y(ym1)

            xp1 = self.periodic_normalize_x(xp1)
            yp1 = self.periodic_normalize_y(yp1)

        # 1 row above current cell
        im1 = i-1
        if im1 < 0:
            im1 = len(state)-1
        if im1 < len(state):
            if state[im1][0] == ym1:
                for k in range(1, len(state[im1])):
                    
                    if state[im1][k] >= xm1 or periodic:

                        # NW
                        if state[im1][k] == xm1:
                            possible_neighbors_list[0] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # N
                        if state[im1][k] == x:
                            possible_neighbors_list[1] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # NE
                        if state[im1][k] == xp1:
                            possible_neighbors_list[2] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

        # The row of the current cell
        for k in range(1, len(state[i])):
            if state[i][k] >= xm1 or periodic:

                # W
                if state[i][k] == xm1:
                    possible_neighbors_list[3] = None
                    neighbors += 1
                    xx = state[i][k]
                    yy = state[i][0]
                    neighborcolor = self.get_cell_color(xx, yy)
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1

                # E
                if state[i][k] == xp1:
                    possible_neighbors_list[4] = None
                    neighbors += 1
                    xx = state[i][k]
                    yy = state[i][0]
                    neighborcolor = self.get_cell_color(xx, yy)
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1

        # 1 row below current cell
        ip1 = i+1
        if ip1 >= len(state):
            ip1 = 0
        if ip1 < len(state):
            if state[ip1][0] == yp1:
                for k in range(1, len(state[ip1])):
                    if state[ip1][k] >= xm1 or periodic:

                        # SW
                        if state[ip1][k] == xm1:
                            possible_neighbors_list[5] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # S
                        if state[ip1][k] == x:
                            possible_neighbors_list[6] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # SE
                        if state[ip1][k] == xp1:
                            possible_neighbors_list[7] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

        color = 0
        if neighbors1 > neighbors2:
            color = 1
        elif neighbors2 > neighbors1:
            color = 2
        else:
            color = -1

        return dict(neighbors=neighbors, color=color)

    def get_color_from_alive(self, x, y):
        """
        This function seems redundant, but is slightly different.
        The above function is for dead cells that become alive.
        This function is for dead cells that come alive because of THOSE cells.
        """
        state1 = self.actual_state1
        state2 = self.actual_state2

        color1 = 0
        color2 = 0

        xm1 = x - 1
        ym1 = y - 1

        xp1 = x + 1
        yp1 = y + 1

        periodic = self.periodic
        if periodic:
            x = self.periodic_normalize_x(x)
            y = self.periodic_normalize_y(y)

            xm1 = self.periodic_normalize_x(xm1)
            ym1 = self.periodic_normalize_y(ym1)

            xp1 = self.periodic_normalize_x(xp1)
            yp1 = self.periodic_normalize_y(yp1)

        # color1
        for i in range(len(state1)):
            yy = state1[i][0]
            if yy == ym1:
                # 1 row above current cell
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # NW
                            color1 += 1
                        elif xx == x:
                            # N
                            color1 += 1
                        elif xx == xp1:
                            # NE
                            color1 += 1

            elif yy == y:
                # Row of current cell
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # W
                            color1 += 1
                        elif xx == xp1:
                            # E
                            color1 += 1

            elif yy == yp1:
                # 1 row below current cell
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # SW
                            color1 += 1
                        elif xx == x:
                            # S
                            color1 += 1
                        elif xx == xp1:
                            # SE
                            color1 += 1

        # color2
        for i in range(len(state2)):
            yy = state2[i][0]
            if yy == ym1:
                # 1 row above current cell
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # NW
                            color2 += 1
                        elif xx == x:
                            # N
                            color2 += 1
                        elif xx == xp1:
                            # NE
                            color2 += 1

            elif yy == y:
                # Row of current cell
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # W
                            color2 += 1
                        elif xx == xp1:
                            # E
                            color2 += 1

            elif yy == yp1:
                # 1 row below current cell
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # SW
                            color2 += 1
                        elif xx == x:
                            # S
                            color2 += 1
                        elif xx == xp1:
                            # SE
                            color2 += 1

        if color1 > color2:
            return 1
        elif color1 < color2:
            return 2
        else:
            return -1

    def is_alive(self, x, y):
        """
        Boolean function: is the cell at x, y alive
        """
        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

        for row in self.actual_state:
            if row[0] == y:
                for c in row[1:]:
                    if c == x:
                        return True

        return False

    def remove_cell(self, x, y, state):
        """
        Remove the given cell from the given listlife state
        """
        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

        for i, row in enumerate(state):
            if row[0] == y:
                if len(row) == 2:
                    # Remove the entire row
                    state = state[:i] + state[i + 1 :]
                    return
                else:
                    j = indexOf(row, x)
                    state[i] = row[:j] + row[j + 1 :]

    def add_cell(self, x, y, state):
        """
        State is a list of arrays, where the y-coordinate is the first element,
        and the rest of the elements are x-coordinates:
          [y1, x1, x2, x3, x4]
          [y2, x5, x6, x7, x8, x9]
          [y3, x10]
        """
        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

        # Empty state case
        if len(state) == 0:
            return [[y, x]]

        # figure out where in the list to insert the new cell
        if y < state[0][0]:
            # y is smaller than any existing y,
            # so put this point at beginning
            return [[y, x]] + state

        elif y > state[-1][0]:
            # y is larger than any existing y,
            # so put this point at end
            return state + [[y, x]]

        else:
            # Adding to the middle
            new_state = []
            added = False
            for row in state:
                if (not added) and (row[0] == y):
                    # This level already exists
                    new_row = [y]
                    for c in row[1:]:
                        if (not added) and (x < c):
                            new_row.append(x)
                            added = True
                        new_row.append(c)
                    if not added:
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

            return new_state

    def approx_equal(self, a, b, tol):
        return self.relative_diff(a, b) < tol

    def relative_diff(self, a, b):
        SMOL = 1e-12
        denom = max(a + SMOL, b + SMOL)
        return abs(a - b) / (1.0 * denom)

    def get_cell_color(self, x, y):
        """
        Get the color of the given cell (1 or 2)
        """
        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

        for row in self.actual_state1:
            if row[0] == y:
                for c in row[1:]:
                    if c == x:
                        return 1
            elif row[0] > y:
                break

        for row in self.actual_state2:
            if row[0] == y:
                for c in row[1:]:
                    if c == x:
                        return 2
            elif row[0] > y:
                break

        return 0

    def get_neighbors_from_alive(self, x, y, i, state, possible_neighbors_list):
        neighbors = 0
        neighbors1 = 0
        neighbors2 = 0

        xm1 = x - 1
        ym1 = y - 1

        xp1 = x + 1
        yp1 = y + 1

        periodic = self.periodic
        if periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

            xm1 = ((x-1) + self.columns)%(self.columns)
            ym1 = ((y-1) + self.rows)%(self.rows)

            xp1 = ((x+1) + self.columns)%(self.columns)
            yp1 = ((y+1) + self.rows)%(self.rows)

        xstencilmin = min(xm1, x, xp1)
        xstencilmax = max(xm1, x, xp1)

        ystencilmin = min(ym1, y, yp1)
        ystencilmax = max(ym1, y, yp1)

        # 1 row above current cell
        im1 = i-1
        if im1 < 0:
            im1 = len(state)-1
        if im1 < len(state):
            if state[im1][0] == ym1:
                for k in range(1, len(state[im1])):
                    
                    if state[im1][k] >= xm1 or periodic:

                        # NW
                        if state[im1][k] == xm1:
                            possible_neighbors_list[0] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # N
                        if state[im1][k] == x:
                            possible_neighbors_list[1] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # NE
                        if state[im1][k] == xp1:
                            possible_neighbors_list[2] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

        # The row of the current cell
        for k in range(1, len(state[i])):
            if state[i][k] >= xm1 or periodic:

                # W
                if state[i][k] == xm1:
                    possible_neighbors_list[3] = None
                    neighbors += 1
                    xx = state[i][k]
                    yy = state[i][0]
                    neighborcolor = self.get_cell_color(xx, yy)
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1

                # E
                if state[i][k] == xp1:
                    possible_neighbors_list[4] = None
                    neighbors += 1
                    xx = state[i][k]
                    yy = state[i][0]
                    neighborcolor = self.get_cell_color(xx, yy)
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1

        # 1 row below current cell
        ip1 = i+1
        if ip1 >= len(state):
            ip1 = 0
        if ip1 < len(state):
            if state[ip1][0] == yp1:
                for k in range(1, len(state[ip1])):
                    if state[ip1][k] >= xm1 or periodic:

                        # SW
                        if state[ip1][k] == xm1:
                            possible_neighbors_list[5] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # S
                        if state[ip1][k] == x:
                            possible_neighbors_list[6] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

                        # SE
                        if state[ip1][k] == xp1:
                            possible_neighbors_list[7] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1

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

    def get_color_from_alive(self, x, y):
        """
        This function seems redundant, but is slightly different.
        The above function is for dead cells that become alive.
        This function is for dead cells that come alive because of THOSE cells.
        """
        state1 = self.actual_state1
        state2 = self.actual_state2

        color1 = 0
        color2 = 0

        xm1 = x - 1
        ym1 = y - 1

        xp1 = x + 1
        yp1 = y + 1

        periodic = self.periodic
        if periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)
            
            xm1 = ((x-1) + self.columns)%(self.columns)
            ym1 = ((y-1) + self.rows)%(self.rows)
            
            xp1 = ((x+1) + self.columns)%(self.columns)
            yp1 = ((y+1) + self.rows)%(self.rows)

        # color1
        for i in range(len(state1)):
            yy = state1[i][0]
            if yy == ym1:
                # 1 row above current cell
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # NW
                            color1 += 1
                        elif xx == x:
                            # N
                            color1 += 1
                        elif xx == xp1:
                            # NE
                            color1 += 1

            elif yy == y:
                # Row of current cell
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # W
                            color1 += 1
                        elif xx == xp1:
                            # E
                            color1 += 1

            elif yy == yp1:
                # 1 row below current cell
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # SW
                            color1 += 1
                        elif xx == x:
                            # S
                            color1 += 1
                        elif xx == xp1:
                            # SE
                            color1 += 1

        # color2
        for i in range(len(state2)):
            yy = state2[i][0]
            if yy == ym1:
                # 1 row above current cell
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # NW
                            color2 += 1
                        elif xx == x:
                            # N
                            color2 += 1
                        elif xx == xp1:
                            # NE
                            color2 += 1

            elif yy == y:
                # Row of current cell
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # W
                            color2 += 1
                        elif xx == xp1:
                            # E
                            color2 += 1

            elif yy == yp1:
                # 1 row below current cell
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            # SW
                            color2 += 1
                        elif xx == x:
                            # S
                            color2 += 1
                        elif xx == xp1:
                            # SE
                            color2 += 1

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

    def periodic_normalize_x(self, x):
        return self._periodic_normalize(x, self.columns)

    def periodic_normalize_y(self, y):
        return self._periodic_normalize(y, self.rows)

    def _periodic_normalize(self, q, p):
        if q >= p or q < 0:
            return (q + p) % (p)
        else:
            return q


