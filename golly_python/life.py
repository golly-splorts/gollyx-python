from .state import LifeState, CompositeLifeState


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
