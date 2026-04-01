import json

EQUALTOL = 1e-8
SMOL = 1e-12

class ToroidalGOL(object):
    ...
    def __init__(
        self,
        s1,
        s2,
        rows: int,
        columns: int,
        rule_b: list = None,
        rule_s: list = None,
        maxdim: int = 280,
        halt: bool = True,
        periodic: bool = True,
        b1: list = [],
        b2: list = [],
        c1: list = [],
        c2: list = [],
    ):
        if isinstance(s1, str):
            s1 = json.loads(s1)
        if isinstance(s2, str):
            s2 = json.loads(s2)

        self.ic1 = s1
        self.ic2 = s2
        self.rows = rows
        self.columns = columns
        self.rule_b = set(rule_b) if rule_b else {3}
        self.rule_s = set(rule_s) if rule_s else {2, 3}
        self.maxdim = maxdim
        self.halt = halt
        self.periodic = periodic
        self.running = True
        self.generation = 0
        self.running_avg_window = [0,]*self.maxdim
        self.running_avg_last3 = [0, 0, 0]
        self.found_victor = False

        # Set-based state: sets of (x, y) tuples
        self.alive = set()
        self.alive1 = set()
        self.alive2 = set()

        # Precompute neighbor offsets
        self._neighbor_offsets = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1),
        ]

        self.prepare()

    def get_live_cells(self):
        live1 = list(self.alive1)
        live2 = list(self.alive2)
        return live1, live2

    def prepare(self):
        s1 = self.ic1
        s2 = self.ic2
        columns = self.columns
        rows = self.rows

        for s1row in s1:
            for y in s1row:
                yy = int(y) % rows
                for xx in s1row[y]:
                    xx = xx % columns
                    self.alive.add((xx, yy))
                    self.alive1.add((xx, yy))

        for s2row in s2:
            for y in s2row:
                yy = int(y) % rows
                for xx in s2row[y]:
                    xx = xx % columns
                    self.alive.add((xx, yy))
                    self.alive2.add((xx, yy))

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    def update_moving_avg(self, livecounts):
        if not self.found_victor:
            maxdim = self.maxdim
            if self.generation < maxdim:
                self.running_avg_window[self.generation] = livecounts["victoryPct"]
            else:
                self.running_avg_window = self.running_avg_window[1:] + [
                    livecounts["victoryPct"]
                ]
                summ = sum(self.running_avg_window)
                running_avg = summ / (1.0 * len(self.running_avg_window))

                removed = self.running_avg_last3[0]
                self.running_avg_last3 = self.running_avg_last3[1:] + [running_avg]

                tol = EQUALTOL
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
        denom = max(abs(a), abs(b), SMOL)
        return (abs(a - b) / denom) < tol

    def _next_generation_logic(self):
        alive = self.alive
        alive1 = self.alive1
        alive2 = self.alive2
        columns = self.columns
        rows = self.rows
        offsets = self._neighbor_offsets
        rule_s = self.rule_s
        rule_b = self.rule_b

        # Count neighbors for all cells adjacent to live cells
        neighbor_count = {}
        for (x, y) in alive:
            for dx, dy in offsets:
                nx = (x + dx) % columns
                ny = (y + dy) % rows
                key = (nx, ny)
                if key in neighbor_count:
                    neighbor_count[key] += 1
                else:
                    neighbor_count[key] = 1

        new_alive = set()
        new_alive1 = set()
        new_alive2 = set()

        # Process all cells that have at least one neighbor
        for (cx, cy), count in neighbor_count.items():
            cell_key = (cx, cy)
            is_alive = cell_key in alive

            if is_alive:
                if count not in rule_s:
                    continue
            else:
                if count not in rule_b:
                    continue

            new_alive.add(cell_key)
            # Determine color by majority of neighbors
            c1 = 0
            c2 = 0
            for dx, dy in offsets:
                nx = (cx + dx) % columns
                ny = (cy + dy) % rows
                nk = (nx, ny)
                if nk in alive1:
                    c1 += 1
                elif nk in alive2:
                    c2 += 1
            if c1 > c2:
                new_alive1.add(cell_key)
            elif c2 > c1:
                new_alive2.add(cell_key)
            elif cx % 2 == cy % 2:
                new_alive1.add(cell_key)
            else:
                new_alive2.add(cell_key)

        self.alive = new_alive
        self.alive1 = new_alive1
        self.alive2 = new_alive2
        return self.get_live_counts()

    def get_live_counts(self):
        livecells = len(self.alive)
        livecells1 = len(self.alive1)
        livecells2 = len(self.alive2)

        self.livecells = livecells
        self.livecells1 = livecells1
        self.livecells2 = livecells2

        victory = 0.0
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
            last3=self.running_avg_last3,
        )

    def next_step(self):
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
