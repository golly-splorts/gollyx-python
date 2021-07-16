from .rules import get_dragon_rules
import json


class BinaryLife(object):

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
    territory1 = 0.0
    territory2 = 0.0

    found_victor: bool = False

    def __init__(
        self,
        ic1: dict,
        ic2: dict,
        rows: int,
        columns: int,
        rule_b: list = [],
        rule_s: list = [],
        halt: bool = True,
    ):
        self.rule = get_random_dragon_rules()

        self.ic1 = ic1
        self.ic2 = ic2

        self.rows = rows
        self.columns = columns

        # Whether to stop when a victor is detected
        self.halt = halt

        self.running = True
        self.generation = 0

        self.found_victor = False

        self.prepare()

    def prepare(self):
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

    def approx_equal(self, a, b, tol):
        SMOL = 1e-12
        return (abs(b - a) / abs(a + SMOL)) < tol

    def is_alive(self, x, y):
        """
        Boolean function: is the cell at x, y alive
        """
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

    def remove_cell(self, x, y, state):
        """
        Remove the given cell from the given listlife state
        """
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

    def next_generation(self):
        """
        Evolve the actual_state list life state to the next generation.
        """
        all_dead_neighbors = {}

        new_state = []
        new_state1 = []
        new_state2 = []

        # The generation tells us which row we're on
        # This is the new row
        ym1 = self.generation
        y = ym1 + 1

        # -------
        # Repeat a procedure 3 times:
        # - once for actual_state
        # - once for actual_state1
        # - once for actual_state2

        # actual_state:

        # Get the index of actual state that corresponds to y-1
        actual_state_prev_ix = -999
        for i in range(len(self.actual_state)):
            if self.actual_state[i][0] == ym1:
                actual_state_prev_ix = i
                break

        # get the x values from row at y-1
        actual_state_prev_xs = []

        # if actual_state_prev_ix is -999, no index found for y-1 b/c
        # not in actual_state, so row has no x values. nothing else to do.

        # otherwise, get x values
        if actual_state_prev_ix != -999:
            actual_state_prev_xs = self.actual_state[actual_state_prev_ix][1:]

        # actual_state1:

        # Get the index of actual state1 that corresponds to y-1
        actual_state1_prev_ix = -999
        for i in range(len(self.actual_state1)):
            if self.actual_state1[i][0] == ym1:
                actual_state1_prev_ix = i
                break

        # get the x values from row at y-1
        actual_state1_prev_xs = []

        # if actual_state1_prev_ix is -999, no index found for y-1 b/c
        # not in actual_state1, so row has no x values. nothing else to do.

        # otherwise, get x values
        if actual_state1_prev_ix != -999:
            actual_state1_prev_xs = self.actual_state1[actual_state1_prev_ix][1:]

        # actual_state2:

        # Get the index of actual state1 that corresponds to y-1
        actual_state2_prev_ix = -999
        for i in range(len(self.actual_state2)):
            if self.actual_state2[i][0] == ym1:
                actual_state2_prev_ix = i
                break

        # get the x values from row at y-1
        actual_state2_prev_xs = []

        # if actual_state2_prev_ix is -999, no index found for y-1 b/c
        # not in actual_state2, so row has no x values. nothing else to do.

        # otherwise, get x values
        if actual_state2_prev_ix != -999:
            actual_state2_prev_xs = self.actual_state2[actual_state2_prev_ix][1:]

        # The procedure we apply is to stride left to right,
        # assembling a key based on cell dead/alive color 1/alive color 2
        # (0 1 2). Using this key and a map, we get the corresponding
        # cell state/color (0 1 2) outcome.
        key = ""

        # ---------------
        # Left boundary
        key = "0"
        for j in range(2):
            if j in actual_state_prev_xs:
                if j in actual_state1_prev_xs:
                    key += "1"
                elif j in actual_state2_prev_xs:
                    key += "2"
                else:
                    key += "0"
            else:
                key += "0"

        left_boundary_state = self.rules[key]
        if left_boundary_state > 0:
            new_state = self.add_cell(0, y, new_state)
            if left_boundary_state == 1:
                new_state1 = self.add_cell(0, y, new_state1)
            elif left_boundary_state == 2:
                new_state2 = self.add_cell(0, y, new_state2)

        # ---------------
        # Internal
        for j in range(1, self.columns - 1):
            key = ""
            for k in range(j - 1, j + 2):
                if k in actual_state_prev_xs:
                    if k in actual_state1_prev_xs:
                        key += "1"
                    elif k in actual_state2_prev_xs:
                        key += "2"
                    else:
                        key += "0"
                else:
                    key += "0"
            cell_state = self.rules.states[key]
            if cell_state > 0:
                new_state = self.add_cell(j, y, new_state)
                if color == 1:
                    new_state1 = self.add_cell(j, y, new_state1)
                elif color == 2:
                    new_state2 = self.add_cell(j, y, new_state2)

        # ---------------
        # Right boundary
        key = ""
        for j in range(self.columns - 2, self.columns):
            if j in actual_state_prev_xs:
                if j in actual_state1_prev_xs:
                    key += "1"
                elif j in actual_state2_prev_xs:
                    key += "2"
                else:
                    key += "0"
            else:
                key += "0"
        key += "0"

        right_boundary_state = self.rules[key]
        if right_boundary_state > 0:
            new_state = self.add_cell(self.columns - 1, y, new_state)
            if right_boundary_state == 1:
                new_state1 = self.add_cell(self.columns - 1, y, new_state1)
            elif right_boundary_state == 2:
                new_state2 = self.add_cell(self.columns - 1, y, new_state2)

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

        territory1 = livecells1 / (1.0 * total_area)
        territory1 = territory1 * 100
        territory2 = livecells2 / (1.0 * total_area)
        territory2 = territory2 * 100
        self.territory1 = territory1
        self.territory2 = territory2

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
            return live_counts


def main():
    gol = BinaryLife(
        s1='[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
        s2='[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
        rows=120,
        columns=100,
    )

    while gol.running:
        gol.next_step()
        if gol.generation % 500 == 0:
            print(f"Simulating generation {gol.generation}")

    from pprint import pprint

    pprint(gol.get_live_counts())


if __name__ == "__main__":
    main()
