import json


class QuaternaryLife(object):

    actual_state: list = []

    actual_state1: list = []
    actual_state2: list = []
    actual_state3: list = []
    actual_state4: list = []

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
    livecells3 = 0
    livecells4 = 0

    victory = 0.0
    coverage = 0.0

    territory1 = 0.0
    territory2 = 0.0
    territory3 = 0.0
    territory4 = 0.0

    found_victor = False
    running_avg_window: list = []
    running_avg_last3: list = [0.0, 0.0, 0.0]
    running = False
    periodic = True

    found_victor: bool = False

    AVGWINDOW = 280

    def __init__(
        self,
        ic1: dict,
        ic2: dict,
        ic3: dict,
        ic4: dict,
        rows: int,
        columns: int,
        rule_b: list = [],
        rule_s: list = [],
        halt: bool = True,
        periodic: bool = True,
    ):
        self.ic1 = ic1
        self.ic2 = ic2
        self.ic3 = ic3
        self.ic4 = ic4

        self.rows = rows
        self.columns = columns

        self.rule_b = rule_b
        self.rule_s = rule_s

        # Whether to stop when a victor is detected
        self.halt = halt

        self.running = True
        self.generation = 0

        self.running_avg_window = [
            0,
        ] * self.AVGWINDOW
        self.running_avg_last3 = [0, 0, 0]
        self.found_victor = False

        self.periodic = periodic

        self.prepare()

    def prepare(self):
        s1 = self.ic1
        s2 = self.ic2
        s3 = self.ic3
        s4 = self.ic4

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

        for s3row in s3:
            for y in s3row:
                yy = int(y)
                for xx in s3row[y]:
                    self.actual_state = self.add_cell(xx, yy, self.actual_state)
                    self.actual_state3 = self.add_cell(xx, yy, self.actual_state3)

        for s4row in s4:
            for y in s4row:
                yy = int(y)
                for xx in s4row[y]:
                    self.actual_state = self.add_cell(xx, yy, self.actual_state)
                    self.actual_state4 = self.add_cell(xx, yy, self.actual_state4)

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    def update_moving_avg(self, livecounts):
        if not self.found_victor:
            maxdim = self.AVGWINDOW
            # maxdim = max(2 * self.columns, 2 * self.rows)
            if self.generation < maxdim:
                self.running_avg_window[self.generation] = livecounts["coverage"]
            else:
                self.running_avg_window = self.running_avg_window[1:] + [
                    livecounts["coverage"]
                ]
                summ = sum(self.running_avg_window)
                running_avg = summ / (1.0 * len(self.running_avg_window))
                # update running average last 3

                removed = self.running_avg_last3[0]
                self.running_avg_last3 = self.running_avg_last3[1:] + [running_avg]

                tol = 1e-8
                # skip the first few steps where we're removing zeros
                if not self.approx_equal(removed, 0.0, tol):
                    # We have a nonzero running average, and no victor,
                    # check if average has become stable
                    b0eq1 = self.approx_equal(
                        self.running_avg_last3[0], self.running_avg_last3[1], tol
                    )
                    b1eq2 = self.approx_equal(
                        self.running_avg_last3[1], self.running_avg_last3[2], tol
                    )
                    victory_by_stability = (b0eq1 and b1eq2) and (
                        livecounts["liveCells"] > 0
                    )
                    if victory_by_stability:
                        # Someone one due to simulation becoming stable
                        ranks = self.get_ranks(livecounts)
                        self.found_victor = True
                        self.running = False

            # end if gen > maxdim
            zero_scores = 0
            if livecounts["liveCells1"] == 0:
                zero_scores += 1
            if livecounts["liveCells2"] == 0:
                zero_scores += 1
            if livecounts["liveCells3"] == 0:
                zero_scores += 1
            if livecounts["liveCells4"] == 0:
                zero_scores += 1
            victory_by_shutout = zero_scores == 3
            if victory_by_shutout:
                ranks = self.get_ranks(livecounts)
                self.found_victor = True
                self.running = False

    def get_ranks(self, livecounts):
        """
        Return an array of 4 elements:
        The ranks of each team
        [team1rank, team2rank, team3rank, team4rank]
        """
        unsorted_scores = [
            livecounts["liveCells1"],
            livecounts["liveCells2"],
            livecounts["liveCells3"],
            livecounts["liveCells4"],
        ]
        sorted_scores = list(reversed(sorted(unsorted_scores)))
        ranks = [3, 3, 3, 3]
        for i, unsorted_score in enumerate(unsorted_scores):
            if unsorted_score > 0:
                ranks[i] = sorted_scores.index(unsorted_score)
        return list(sorted_scores)

    def approx_equal(self, a, b, tol):
        SMOL = 1e-12
        return (abs(b - a) / abs(a + SMOL)) < tol

    def is_alive(self, x, y):
        """
        Boolean function: is the cell at x, y alive
        """
        if self.periodic:
            x = (x + self.columns) % (self.columns)
            y = (y + self.rows) % (self.rows)

        for row in self.actual_state:
            if row[0] == y:
                for c in row[1:]:
                    if c == x:
                        return True

        return False

    def get_cell_color(self, x, y):
        """
        Get the color of the given cell (1 or 2)
        """
        if self.periodic:
            x = (x + self.columns) % (self.columns)
            y = (y + self.rows) % (self.rows)

        states = [
            self.actual_state1,
            self.actual_state2,
            self.actual_state3,
            self.actual_state4,
        ]
        for i in range(len(states)):
            state = states[i]
            for row in state:
                if row[0] == y:
                    for c in row[1:]:
                        if c == x:
                            return i + 1
                elif row[0] > y:
                    break

        return 0

    def remove_cell(self, x, y, state):
        """
        Remove the given cell from the given listlife state
        """
        if self.periodic:
            x = (x + self.columns) % (self.columns)
            y = (y + self.rows) % (self.rows)

        for i, row in enumerate(state):
            if row[0] == y:
                if len(row) == 2:
                    # Remove the entire row
                    state = state[:i] + state[i + 1 :]
                    return
                else:
                    j = row.index(x)
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
            x = (x + self.columns) % (self.columns)
            y = (y + self.rows) % (self.rows)

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

    def get_neighbors_from_alive(self, x, y, i, state, possible_neighbors_list):
        neighbors = 0
        neighbors_counter = [0, 0, 0, 0]

        xm1 = x - 1
        ym1 = y - 1

        xp1 = x + 1
        yp1 = y + 1

        periodic = self.periodic
        if periodic:
            x = (x + self.columns) % (self.columns)
            y = (y + self.rows) % (self.rows)

            xm1 = ((x - 1) + self.columns) % (self.columns)
            ym1 = ((y - 1) + self.rows) % (self.rows)

            xp1 = ((x + 1) + self.columns) % (self.columns)
            yp1 = ((y + 1) + self.rows) % (self.rows)

        xstencilmin = min(xm1, x, xp1)
        xstencilmax = max(xm1, x, xp1)

        ystencilmin = min(ym1, y, yp1)
        ystencilmax = max(ym1, y, yp1)

        # 1 row above current cell
        im1 = i - 1
        if im1 < 0:
            im1 = len(state) - 1
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
                            if neighborcolor > 0:
                                neighbors_counter[neighborcolor - 1] += 1

                        # N
                        if state[im1][k] == x:
                            possible_neighbors_list[1] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor > 0:
                                neighbors_counter[neighborcolor - 1] += 1

                        # NE
                        if state[im1][k] == xp1:
                            possible_neighbors_list[2] = None
                            neighbors += 1
                            xx = state[im1][k]
                            yy = state[im1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor > 0:
                                neighbors_counter[neighborcolor - 1] += 1

                        # Break it off early
                        if not periodic and state[im1][k] > xp1:
                            break

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
                    if neighborcolor > 0:
                        neighbors_counter[neighborcolor - 1] += 1

                # E
                if state[i][k] == xp1:
                    possible_neighbors_list[4] = None
                    neighbors += 1
                    xx = state[i][k]
                    yy = state[i][0]
                    neighborcolor = self.get_cell_color(xx, yy)
                    if neighborcolor > 0:
                        neighbors_counter[neighborcolor - 1] += 1

                # Break it off early
                if not periodic and state[i][k] > xp1:
                    break

        # 1 row below current cell
        ip1 = i + 1
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
                            if neighborcolor > 0:
                                neighbors_counter[neighborcolor - 1] += 1

                        # S
                        if state[ip1][k] == x:
                            possible_neighbors_list[6] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor > 0:
                                neighbors_counter[neighborcolor - 1] += 1

                        # SE
                        if state[ip1][k] == xp1:
                            possible_neighbors_list[7] = None
                            neighbors += 1
                            xx = state[ip1][k]
                            yy = state[ip1][0]
                            neighborcolor = self.get_cell_color(xx, yy)
                            if neighborcolor > 0:
                                neighbors_counter[neighborcolor - 1] += 1

                        # Break it off early
                        if not periodic and state[ip1][k] > xp1:
                            break

        color = 0
        if sum(neighbors_counter) > 0:
            color = 1 + neighbors_counter.index(max(neighbors_counter))

        return dict(neighbors=neighbors, color=color)

    def get_color_from_alive(self, x, y):
        """
        This function seems redundant, but is slightly different.
        The above function is for dead cells that become alive.
        This function is for dead cells that come alive because of THOSE cells.
        """
        states = [
            self.actual_state1,
            self.actual_state2,
            self.actual_state3,
            self.actual_state4,
        ]
        colors_counter = [0, 0, 0, 0]

        xm1 = x - 1
        ym1 = y - 1

        xp1 = x + 1
        yp1 = y + 1

        periodic = self.periodic
        if periodic:
            x = (x + self.columns) % (self.columns)
            y = (y + self.rows) % (self.rows)

            xm1 = ((x - 1) + self.columns) % (self.columns)
            ym1 = ((y - 1) + self.rows) % (self.rows)

            xp1 = ((x + 1) + self.columns) % (self.columns)
            yp1 = ((y + 1) + self.rows) % (self.rows)

        for s in range(len(states)):
            state = states[s]

            for i in range(len(state)):
                yy = state[i][0]
                if yy == ym1:
                    # 1 row above current cell
                    for j in range(1, len(state[i])):
                        xx = state[i][j]
                        if xx >= xm1 or periodic:
                            if xx == xm1:
                                # NW
                                colors_counter[s] += 1
                            elif xx == x:
                                # N
                                colors_counter[s] += 1
                            elif xx == xp1:
                                # NE
                                colors_counter[s] += 1
                        if not periodic and xx >= xp1:
                            break

                elif yy == y:
                    # Row of current cell
                    for j in range(1, len(state[i])):
                        xx = state[i][j]
                        if xx >= xm1 or periodic:
                            if xx == xm1:
                                # W
                                colors_counter[s] += 1
                            elif xx == xp1:
                                # E
                                colors_counter[s] += 1
                        if not periodic and xx >= xp1:
                            break

                elif yy == yp1:
                    # 1 row below current cell
                    for j in range(1, len(state[i])):
                        xx = state[i][j]
                        if xx >= xm1 or periodic:
                            if xx == xm1:
                                # SW
                                colors_counter[s] += 1
                            elif xx == x:
                                # S
                                colors_counter[s] += 1
                            elif xx == xp1:
                                # SE
                                colors_counter[s] += 1
                        if not periodic and xx >= xp1:
                            break

        color = 0
        if sum(colors_counter) > 0:
            color = 1 + colors_counter.index(max(colors_counter))

        return color

    def next_generation(self):
        """
        Evolve the actual_state list life state to the next generation.
        """
        all_dead_neighbors = {}

        new_state = []

        new_states = [[], [], [], []]

        for i in range(len(self.actual_state)):
            self.top_pointer = 1
            self.bottom_pointer = 1

            for j in range(1, len(self.actual_state[i])):
                x = self.actual_state[i][j]
                y = self.actual_state[i][0]

                xm1 = x - 1
                ym1 = y - 1

                xp1 = x + 1
                yp1 = y + 1

                if self.periodic:

                    x = (x + self.columns) % (self.columns)
                    y = (y + self.rows) % (self.rows)

                    xm1 = ((x - 1) + self.columns) % (self.columns)
                    ym1 = ((y - 1) + self.rows) % (self.rows)

                    xp1 = ((x + 1) + self.columns) % (self.columns)
                    yp1 = ((y + 1) + self.rows) % (self.rows)

                # create a list of possible dead neighbors
                # get_neighbors_from_alive() will pare this down
                dead_neighbors = [
                    [xm1, ym1, 1],
                    [x, ym1, 1],
                    [xp1, ym1, 1],
                    [xm1, y, 1],
                    [xp1, y, 1],
                    [xm1, yp1, 1],
                    [x, yp1, 1],
                    [xp1, yp1, 1],
                ]

                result = self.get_neighbors_from_alive(
                    x, y, i, self.actual_state, dead_neighbors
                )
                neighbors = result["neighbors"]
                if neighbors == 2:
                    # Tie, keep current color
                    color = self.get_cell_color(x, y)
                else:
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
                    # Keep cell alive
                    new_state = self.add_cell(x, y, new_state)
                    if color > 0:
                        state = new_states[color-1]
                        state = self.add_cell(x, y, state)
                        new_states[color-1] = state
                else:
                    # Kill cell
                    pass

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
                if color > 0:
                    state = new_states[color-1]
                    state = self.add_cell(t1, t2, state)
                    new_states[color-1] = state

        self.actual_state = new_state

        (self.actual_state1, self.actual_state2, self.actual_state3, self.actual_state4) = new_states

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
        livecells3 = _count_live_cells(self.actual_state3)
        livecells4 = _count_live_cells(self.actual_state4)

        self.livecells = livecells
        self.livecells1 = livecells1
        self.livecells2 = livecells2
        self.livecells3 = livecells3
        self.livecells4 = livecells4

        SMOL = 1e-12

        total_area = self.columns * self.rows
        coverage = livecells / (1.0 * total_area)
        coverage = coverage * 100
        self.coverage = coverage

        return dict(
            generation=self.generation,
            liveCells=livecells,
            liveCells1=livecells1,
            liveCells2=livecells2,
            liveCells3=livecells3,
            liveCells4=livecells4,
            coverage=coverage,
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


def main():
    ics = [
        '[{"50":[60,160]},{"51":[62,162]},{"52":[59,60,63,64,65,159,160,163,164,165]}]',
        '[{"60":[60,160]},{"61":[62,162]},{"62":[59,60,63,64,65,159,160,163,164,165]}]',
        '[{"31":[29,30,33,34,35,129,130,133,134,135]},{"32":[32,132]},{"33":[30,130]}]',
        '[{"61":[29,30,33,34,35,129,130,133,134,135]},{"62":[32,132]},{"63":[30,130]}]',
    ]
    states = [
        json.loads(ics[i]) for i in range(len(ics))
    ]
    gol = QuaternaryLife(
        *states,
        rows=120,
        columns=180,
    )

    while gol.running:
        gol.next_step()
        if gol.generation % 500 == 0:
            print(f"Simulating generation {gol.generation}")

    from pprint import pprint

    pprint(gol.get_live_counts())


if __name__ == "__main__":
    main()
