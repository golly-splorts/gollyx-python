from operator import indexOf
from .utils import lists_equal
from .linkedlists import LifeList


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
