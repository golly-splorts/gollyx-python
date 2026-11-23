import math
import json
from array import array


# Default value for dimension (in time) of time-average window
MAXDIM = 280

# Packed neighbor counts: bits 0-3 total, bits 4-7 team 1, bits 8-11 team 2 (referees count toward the total only)
INC_C1 = 0x011
INC_C2 = 0x101
INC_REF = 0x001


class StarGOL(object):
    """
    Star Wars style Generations cellular automaton (default B2/S345/C4) with two teams and referees,
    on a periodic (toroidal) board.

    Cell state lives in flat buffers indexed y * columns + x:
    _state is 0 for dead, 1 for alive, 2 + k for dead-wait phase k; _color is 1 (team 1),
    2 (team 2) or 3 (referee) for alive and dead-wait cells, 0 for dead cells.
    """

    who_won = 0

    def __init__(
        self,
        s1=[],
        s2=[],
        rows: int = 0,
        columns: int = 0,
        rule_b: list = None,
        rule_s: list = None,
        rule_c: int = 4,
        periodic: bool = True,
        maxdim: int = MAXDIM,
        b1: list = [],
        b2: list = [],
        c1: list = [],
        c2: list = [],
        **kwargs,
    ):
        """
        Args:
            s1 (list or str): team 1 live cells, [{"y": [x, ...]}, ...] or its JSON string.
            s2 (list or str): team 2 live cells, same format.
            rows (int): board rows.
            columns (int): board columns.
            rule_b (list of int): neighbor counts that cause birth (default [3]).
            rule_s (list of int): neighbor counts that allow survival (default [2, 3]).
            rule_c (int): number of states; dying cells wait rule_c - 2 phases before rebirth (at least 3).
            periodic (bool): must be True; the board always wraps.
            maxdim (int): length of the moving-average window, in generations.
            b1, b2 (list or str): team 1/2 cells starting in dead-wait phase 0.
            c1, c2 (list or str): team 1/2 cells starting in dead-wait phase 1.
            tol_zero (float, keyword): tolerance for a zero running average (default 1e-8).
            tol_stable (float, keyword): tolerance for a stable running average (default 1e-6).

        Raises:
            ValueError: if periodic is False or rule_c is below 3.
        """
        if isinstance(s1, str):
            s1 = json.loads(s1)
        if isinstance(s2, str):
            s2 = json.loads(s2)
        if isinstance(b1, str):
            b1 = json.loads(b1)
        if isinstance(b2, str):
            b2 = json.loads(b2)
        if isinstance(c1, str):
            c1 = json.loads(c1)
        if isinstance(c2, str):
            c2 = json.loads(c2)

        self.rows = rows
        self.columns = columns
        self.width = columns
        self.height = rows

        self.rule_b = rule_b or [3]
        self.rule_s = rule_s or [2, 3]
        if rule_c < 3:
            raise ValueError("StarGOL requires rule_c >= 3")
        self.rule_c = rule_c
        self.ndw = rule_c - 2

        self.maxdim = maxdim
        self.halt = True
        self.periodic = periodic

        self.tol_zero = kwargs.get("tol_zero", 1e-8)
        self.tol_stable = kwargs.get("tol_stable", 1e-6)

        # Survive/birth lookup by number of alive neighbors
        self._survive = bytearray(9)
        self._born = bytearray(9)
        for n in self.rule_s:
            if 0 <= n <= 8:
                self._survive[n] = 1
        for n in self.rule_b:
            if 0 <= n <= 8:
                self._born[n] = 1

        sz = rows * columns
        self.sz = sz
        self.total_area = columns * rows

        # Flat neighbor table: 8 neighbors per cell, NW N NE W E SW S SE
        nt = array('l', [0] * (sz * 8))
        for y in range(rows):
            ym1 = ((y - 1) % rows) * columns
            yy = y * columns
            yp1 = ((y + 1) % rows) * columns
            for x in range(columns):
                base = (yy + x) * 8
                xm1 = (x - 1) % columns
                xp1 = (x + 1) % columns
                nt[base] = ym1 + xm1
                nt[base + 1] = ym1 + x
                nt[base + 2] = ym1 + xp1
                nt[base + 3] = yy + xm1
                nt[base + 4] = yy + xp1
                nt[base + 5] = yp1 + xm1
                nt[base + 6] = yp1 + x
                nt[base + 7] = yp1 + xp1
        self._nt = nt

        self._combo_buf = array('l', [0] * sz)
        self._dirty = array('l', [0] * sz)

        self.set_pattern(s1, s2, b1, b2, c1, c2)

    @property
    def periodic(self):
        return True

    @periodic.setter
    def periodic(self, value):
        # The neighbor table always wraps around the board edges
        if not value:
            raise ValueError("StarGOL only supports periodic=True")

    def set_pattern(self, pattern_color1, pattern_color2, pattern_b1=[], pattern_b2=[], pattern_c1=[], pattern_c2=[]):
        """
        Reset the board and load initial conditions. Team 1 wins overlaps; a dead-wait cell is
        skipped if its cell is already alive or holds an earlier phase.

        Args:
            pattern_color1, pattern_color2 (list): team 1/2 live cells, [{"y": [x, ...]}, ...].
            pattern_b1, pattern_b2 (list): team 1/2 cells in dead-wait phase 0.
            pattern_c1, pattern_c2 (list): team 1/2 cells in dead-wait phase 1.
        """
        sz = self.sz
        self._state = bytearray(sz)
        self._color = bytearray(sz)
        self.live_c1 = []
        self.live_c2 = []
        self.live_ref = []
        self._dw = [[] for _ in range(self.ndw)]
        self.generation = 0
        self.running_avg_window = [0] * self.maxdim
        self.running_avg_last3 = [0, 0, 0]
        self.found_victor = False
        self.running = True

        self._load_cells(pattern_color1, 1, 1, self.live_c1)
        self._load_cells(pattern_color2, 2, 1, self.live_c2)
        for pattern_data, color, phase in ((pattern_b1, 1, 0), (pattern_b2, 2, 0), (pattern_c1, 1, 1), (pattern_c2, 2, 1)):
            if phase < self.ndw:
                self._load_cells(pattern_data, color, phase + 2, self._dw[phase])

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    def _load_cells(self, pattern, color, state_value, cell_list):
        """
        Place cells from a pattern into empty board cells.

        Args:
            pattern (list): cells, [{"y": [x, ...]}, ...].
            color (int): color to give the cells (1 or 2).
            state_value (int): _state value to give the cells (1 alive, 2 + k dead-wait phase k).
            cell_list (list of int): list that receives the flat indices of placed cells.
        """
        rows = self.rows
        columns = self.columns
        state = self._state
        colors = self._color
        for row in pattern:
            for y, xs in row.items():
                yy = (int(y) % rows) * columns
                for x in xs:
                    idx = yy + x % columns
                    if state[idx] == 0:
                        state[idx] = state_value
                        colors[idx] = color
                        cell_list.append(idx)

    def check_for_victor(self):
        return self.found_victor

    def update_moving_avg(self, livecounts=None):
        """
        Update the moving average of sqrt(team1^2 + team2^2) and declare a victor on stability or shutout.

        Args:
            livecounts (dict): output of get_live_counts() for the current generation (computed if None).
        """
        if livecounts is None:
            livecounts = self.get_live_counts()

        if not self.found_victor:
            maxdim = self.maxdim

            rootsum = 0
            # This should be 2, not 3 (refs don't count)
            for i in range(2):
                rootsum += livecounts['liveCellsColors'][i]**2
            rootsum = math.sqrt(rootsum)

            if self.generation < maxdim:
                self.running_avg_window[self.generation] = rootsum
            else:
                self.running_avg_window = self.running_avg_window[1:] + [rootsum]
                summ = sum(self.running_avg_window)
                running_avg = summ / (1.0*len(self.running_avg_window))

                # update running average last 3
                removed = self.running_avg_last3[0]
                self.running_avg_last3 = self.running_avg_last3[1:] + [running_avg]

                tol_zero = self.tol_zero
                tol_stable = self.tol_stable

                # skip the first few steps where we're removing zeros
                if not self.approx_equal(removed, 0.0, tol_zero):
                    b1 = self.approx_equal(
                        self.running_avg_last3[0], self.running_avg_last3[1], tol_stable
                    )
                    b2 = self.approx_equal(
                        self.running_avg_last3[1], self.running_avg_last3[2], tol_stable
                    )
                    victory_by_stability = (b1 and b2) and (livecounts['liveCells'] > 0)

                    if victory_by_stability:
                        self.found_victor = True
                        if livecounts["liveCellsColors"][0] > livecounts["liveCellsColors"][1]:
                            self.who_won = 1
                        elif livecounts["liveCellsColors"][0] < livecounts["liveCellsColors"][1]:
                            self.who_won = 2
                        else:
                            self.who_won = -1

            # A team shut out ends the game; before maxdim generations it counts as a tie
            if livecounts["liveCellsColors"][0] == 0 or livecounts["liveCellsColors"][1] == 0:
                self.found_victor = True
                if self.generation < maxdim:
                    self.who_won = -1
                else:
                    if livecounts["liveCellsColors"][0] > livecounts["liveCellsColors"][1]:
                        self.who_won = 1
                    elif livecounts["liveCellsColors"][0] < livecounts["liveCellsColors"][1]:
                        self.who_won = 2
                    else:
                        self.who_won = -1

    def next_step(self):
        """
        Advance the simulation one generation (unless halted after a victor).

        Returns:
            dict: get_live_counts() after the step.
        """
        if self.running is False:
            return self.get_live_counts()
        elif self.halt and self.found_victor:
            self.running = False
            return self.get_live_counts()
        else:
            self.generation += 1
            live_counts = self._next_generation_logic()
            self.update_moving_avg(live_counts)
            return live_counts

    def next_generation(self):
        """
        Same as next_step().

        Returns:
            dict: get_live_counts() after the step.
        """
        return self.next_step()

    def _next_generation_logic(self):
        """
        Advance the board one generation.

        Alive cells take the majority color of their alive team neighbors; a tie above zero goes to
        the majority of dead-wait team neighbors, and a second tie (or no alive team neighbors)
        keeps the cell's color. Survivors stay alive with that color, the rest enter dead-wait
        phase 0 with it. Dead cells outside dead-wait with a birth count come alive with the
        majority team color, or as referees on a tie. Dead-wait phases then advance by one.

        Returns:
            dict: get_live_counts() for the new generation.
        """
        state = self._state
        color = self._color
        nt = self._nt
        cb = self._combo_buf
        dirty = self._dirty
        survive = self._survive
        born = self._born
        dc = 0

        live_c1 = self.live_c1
        live_c2 = self.live_c2
        live_ref = self.live_ref

        # Scatter packed alive-neighbor counts, tracking every touched cell
        for cells, inc in ((live_c1, INC_C1), (live_c2, INC_C2), (live_ref, INC_REF)):
            for idx in cells:
                base = idx * 8
                n = nt[base]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc
                n = nt[base + 1]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc
                n = nt[base + 2]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc
                n = nt[base + 3]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc
                n = nt[base + 4]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc
                n = nt[base + 5]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc
                n = nt[base + 6]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc
                n = nt[base + 7]
                if cb[n] == 0: dirty[dc] = n; dc += 1
                cb[n] += inc

        new_c1 = []
        new_c2 = []
        new_ref = []
        dying = []

        # Survive step: dying cells keep state 1 until the dead-wait cycle below,
        # so tiebreaks only see cells that were already in dead-wait
        for cells, own in ((live_c1, 1), (live_c2, 2), (live_ref, 3)):
            for idx in cells:
                p = cb[idx]
                n1 = (p >> 4) & 15
                n2 = (p >> 8) & 15
                if n1 > n2:
                    c = 1
                elif n2 > n1:
                    c = 2
                elif n1 > 0:
                    base = idx * 8
                    dw1 = 0
                    dw2 = 0
                    for m in range(base, base + 8):
                        k = nt[m]
                        if state[k] >= 2:
                            kc = color[k]
                            if kc == 1:
                                dw1 += 1
                            elif kc == 2:
                                dw2 += 1
                    if dw1 > dw2:
                        c = 1
                    elif dw2 > dw1:
                        c = 2
                    else:
                        c = own
                else:
                    c = own

                if survive[p & 15]:
                    if c == 1:
                        new_c1.append(idx)
                    elif c == 2:
                        new_c2.append(idx)
                    else:
                        new_ref.append(idx)
                else:
                    color[idx] = c
                    dying.append(idx)

        # Birth step: touched cells that are fully dead, then clear the counts
        for i in range(dc):
            idx = dirty[i]
            p = cb[idx]
            cb[idx] = 0
            if state[idx] == 0 and born[p & 15]:
                n1 = (p >> 4) & 15
                n2 = (p >> 8) & 15
                if n1 > n2:
                    new_c1.append(idx)
                elif n2 > n1:
                    new_c2.append(idx)
                else:
                    new_ref.append(idx)

        for idx in new_c1:
            state[idx] = 1
            color[idx] = 1
        for idx in new_c2:
            state[idx] = 1
            color[idx] = 2
        for idx in new_ref:
            state[idx] = 1
            color[idx] = 3

        # Dead-wait cycle: the last phase dies, the others advance, the dying enter phase 0
        dw = self._dw
        last = self.ndw - 1
        for idx in dw[last]:
            state[idx] = 0
            color[idx] = 0
        for ph in range(last, 0, -1):
            cells = dw[ph - 1]
            sv = ph + 2
            for idx in cells:
                state[idx] = sv
            dw[ph] = cells
        for idx in dying:
            state[idx] = 2
        dw[0] = dying

        self.live_c1 = new_c1
        self.live_c2 = new_c2
        self.live_ref = new_ref

        return self.get_live_counts()

    def get_live_cells(self):
        """
        Return the coordinates of all live cells for each color.

        Returns:
            tuple: three lists of (x, y) int tuples, for team 1, team 2 and referees.
        """
        columns = self.columns
        return tuple(
            [(idx % columns, idx // columns) for idx in cells]
            for cells in (self.live_c1, self.live_c2, self.live_ref)
        )

    def get_dead_wait_cells(self):
        """
        Return the coordinates of all dead-wait cells, by phase and color.

        Returns:
            list: one entry per dead-wait phase (rule_c - 2 phases, phase 0 first).
                Each entry is a 3-tuple of sorted lists of (x, y) int tuples, for
                colors 1, 2 and 3 (referee).
        """
        columns = self.columns
        color = self._color
        result = []
        for cells in self._dw:
            per_color = ([], [], [])
            for idx in cells:
                per_color[color[idx] - 1].append((idx % columns, idx // columns))
            result.append(tuple(sorted(c) for c in per_color))
        return result

    def get_live_counts(self):
        """
        Returns:
            dict: generation (int), liveCells (int), liveCells1 (int), liveCells2 (int),
                liveCellsColors (list of 3 ints: team 1, team 2, referees), coverage (float, percent
                of the board alive), last3 (list of the last three running averages).
        """
        lc1 = len(self.live_c1)
        lc2 = len(self.live_c2)
        lcr = len(self.live_ref)
        livecells = lc1 + lc2 + lcr

        total_area = self.total_area
        coverage = (livecells / (1.0 * total_area)) * 100 if total_area > 0 else 0
        self.coverage = coverage

        return dict(
            generation=self.generation,
            liveCells=livecells,
            liveCells1=lc1,
            liveCells2=lc2,
            liveCellsColors=[lc1, lc2, lcr],
            coverage=coverage,
            last3=self.running_avg_last3,
        )

    def _index(self, x, y):
        return (y % self.rows) * self.columns + (x % self.columns)

    def is_alive(self, x, y):
        """
        Returns:
            bool: True if cell (x, y) is alive (coordinates wrap).
        """
        return self._state[self._index(x, y)] == 1

    def is_dead_wait(self, x, y):
        """
        Returns:
            bool: True if cell (x, y) is in any dead-wait phase (coordinates wrap).
        """
        return self._state[self._index(x, y)] >= 2

    def get_cell_color(self, x, y):
        """
        Returns:
            int: color of alive cell (x, y) (1, 2 or 3), or 0 if it is not alive (coordinates wrap).
        """
        idx = self._index(x, y)
        return self._color[idx] if self._state[idx] == 1 else 0

    def approx_equal(self, a, b, tol):
        return self.relative_diff(a, b) < tol

    def relative_diff(self, a, b):
        SMOL = 1e-12
        denom = max(abs(a), abs(b), SMOL)
        return abs(a - b) / denom
