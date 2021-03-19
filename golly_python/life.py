from .constants import EQUALTOL, SMOL
from .state import LifeState, BinaryLifeState
from .stats import LifeStats


class BinaryLife(object):
    """
    Class to manage the state of a binary game of life.
    """
    actual_state: BinaryLifeState
    actual_state1: LifeState
    actual_state2: LifeState

    generation = 0
    columns = 0
    rows = 0

    found_victor: bool = False
    running: bool = False
    neighbor_color_legacy_mode: bool = False

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

        self.neighbor_color_legacy_mode = neighbor_color_legacy_mode

        # Whether to stop when a victor is detected
        self.halt = halt
        self.found_victor = False

        self.running = True
        self.generation = 0
        self.stats = LifeStats(self)

        self.actual_state1 = LifeState(rows, columns, neighbor_color_legacy_mode)
        self.actual_state2 = LifeState(rows, columns, neighbor_color_legacy_mode)
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

    def next_step(self):
        """Advance the state of the simulator forward by one time step"""
        if self.running is False:
            return self.get_stats()
        elif self.halt and self.found_victor:
            self.running = False
            return self.get_stats()
        else:
            self.generation += 1
            live_counts = self._next_generation()
            # Method above will call stats.get_live_counts()
            self.stats.update_moving_avg()
            return live_counts

    def _next_generation(self):
        """Advance life to the next generation"""
        all_dead_neighbors = {}

        new_state1 = LifeState(self.rows, self.columns)
        new_state2 = LifeState(self.rows, self.columns)
        new_state = BinaryLifeState(new_state1, new_state2)

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

        return self.get_stats()

    def get_stats(self):
        """
        Get live counts of cells of each color, and total.
        Compute statistics.
        """
        return self.stats.get_live_counts(
            self.actual_state, self.actual_state1, self.actual_state2, self.generation
        )