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
            if self.check_for_victor():
                self.running = False
            return live_counts

    def check_for_victor(self):
        if self.stats.found_victor:
            return True
        else:
            return 0

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
