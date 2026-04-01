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

        sz = rows * columns
        self.sz = sz
        # grid1[idx] = 1 if team1, grid2[idx] = 1 if team2
        self.grid1 = bytearray(sz)
        self.grid2 = bytearray(sz)
        # List of linear indices of all live cells
        self.live_cells = []

        # Precompute neighbor offset table: for each linear index, store 8 neighbor indices
        self._neighbor_offsets = []
        for y in range(rows):
            for x in range(columns):
                xm1 = (x - 1) % columns
                xp1 = (x + 1) % columns
                ym1 = (y - 1) % rows
                yp1 = (y + 1) % rows
                self._neighbor_offsets.append((
                    ym1 * columns + xm1, ym1 * columns + x, ym1 * columns + xp1,
                    y * columns + xm1,                       y * columns + xp1,
                    yp1 * columns + xm1, yp1 * columns + x, yp1 * columns + xp1,
                ))

        # Precompute checkerboard
        self._checker = bytearray(sz)
        for y in range(rows):
            for x in range(columns):
                if x % 2 == y % 2:
                    self._checker[y * columns + x] = 1

        self.prepare()

    def prepare(self):
        s1 = self.ic1
        s2 = self.ic2
        columns = self.columns
        rows = self.rows
        g1 = self.grid1
        g2 = self.grid2
        live = []

        for s1row in s1:
            for y_str in s1row:
                y = int(y_str) % rows
                for x in s1row[y_str]:
                    x = x % columns
                    idx = y * columns + x
                    g1[idx] = 1
                    live.append(idx)

        for s2row in s2:
            for y_str in s2row:
                y = int(y_str) % rows
                for x in s2row[y_str]:
                    x = x % columns
                    idx = y * columns + x
                    g2[idx] = 1
                    live.append(idx)

        self.live_cells = live
        livecounts = self._get_live_counts_internal()
        self._update_moving_avg(livecounts)

    def get_live_cells(self):
        columns = self.columns
        g1 = self.grid1
        live1 = []
        live2 = []
        for idx in self.live_cells:
            x = idx % columns
            y = idx // columns
            if g1[idx]:
                live1.append((x, y))
            else:
                live2.append((x, y))
        return live1, live2

    def _update_moving_avg(self, livecounts):
        if self.found_victor:
            return
        maxdim = self.maxdim
        gen = self.generation
        victoryPct = livecounts[4]
        if gen < maxdim:
            self.running_avg_window[gen] = victoryPct
        else:
            w = self.running_avg_window
            w.pop(0)
            w.append(victoryPct)
            running_avg = sum(w) / (1.0 * len(w))

            removed = self.running_avg_last3[0]
            self.running_avg_last3 = [self.running_avg_last3[1], self.running_avg_last3[2], running_avg]

            tol = EQUALTOL
            smol = SMOL
            denom = max(abs(removed), smol)
            if not ((abs(removed) / denom) < tol):
                ra = self.running_avg_last3
                d01 = abs(ra[0] - ra[1])
                mx01 = max(abs(ra[0]), abs(ra[1]), smol)
                b1 = (d01 / mx01) < tol
                d12 = abs(ra[1] - ra[2])
                mx12 = max(abs(ra[1]), abs(ra[2]), smol)
                b2 = (d12 / mx12) < tol

                lc1 = livecounts[2]
                lc2 = livecounts[3]
                zerocells = lc1 == 0 or lc2 == 0

                if (b1 and b2) or zerocells:
                    d050 = abs(ra[0] - 50.0)
                    mx050 = max(abs(ra[0]), 50.0, smol)
                    z1 = (d050 / mx050) < tol
                    d150 = abs(ra[1] - 50.0)
                    mx150 = max(abs(ra[1]), 50.0, smol)
                    z2 = (d150 / mx150) < tol
                    d250 = abs(ra[2] - 50.0)
                    mx250 = max(abs(ra[2]), 50.0, smol)
                    z3 = (d250 / mx250) < tol
                    if (not (z1 or z2 or z3)) or zerocells:
                        if lc1 > lc2:
                            self.found_victor = True
                            self.who_won = 1
                        elif lc1 < lc2:
                            self.found_victor = True
                            self.who_won = 2

    def _next_generation_logic(self):
        g1 = self.grid1
        g2 = self.grid2
        offsets = self._neighbor_offsets
        checker = self._checker
        rule_s = self.rule_s
        rule_b = self.rule_b

        # For each cell adjacent to a live cell, count total neighbors and c1 neighbors
        counts = {}
        counts_get = counts.get

        for idx in self.live_cells:
            is_c1 = g1[idx]
            n0, n1, n2, n3, n4, n5, n6, n7 = offsets[idx]

            if is_c1:
                v = counts_get(n0)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n0] = [1, 1]
                v = counts_get(n1)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n1] = [1, 1]
                v = counts_get(n2)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n2] = [1, 1]
                v = counts_get(n3)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n3] = [1, 1]
                v = counts_get(n4)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n4] = [1, 1]
                v = counts_get(n5)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n5] = [1, 1]
                v = counts_get(n6)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n6] = [1, 1]
                v = counts_get(n7)
                if v is not None: v[0] += 1; v[1] += 1
                else: counts[n7] = [1, 1]
            else:
                v = counts_get(n0)
                if v is not None: v[0] += 1
                else: counts[n0] = [1, 0]
                v = counts_get(n1)
                if v is not None: v[0] += 1
                else: counts[n1] = [1, 0]
                v = counts_get(n2)
                if v is not None: v[0] += 1
                else: counts[n2] = [1, 0]
                v = counts_get(n3)
                if v is not None: v[0] += 1
                else: counts[n3] = [1, 0]
                v = counts_get(n4)
                if v is not None: v[0] += 1
                else: counts[n4] = [1, 0]
                v = counts_get(n5)
                if v is not None: v[0] += 1
                else: counts[n5] = [1, 0]
                v = counts_get(n6)
                if v is not None: v[0] += 1
                else: counts[n6] = [1, 0]
                v = counts_get(n7)
                if v is not None: v[0] += 1
                else: counts[n7] = [1, 0]

        # Build new state
        new_g1 = bytearray(len(g1))
        new_g2 = bytearray(len(g2))
        new_live = []
        new_live_append = new_live.append

        for idx, val in counts.items():
            total = val[0]
            is_alive = g1[idx] or g2[idx]

            if is_alive:
                if total not in rule_s:
                    continue
            else:
                if total not in rule_b:
                    continue

            new_live_append(idx)
            c1 = val[1]
            c2 = total - c1
            if c1 > c2:
                new_g1[idx] = 1
            elif c2 > c1:
                new_g2[idx] = 1
            elif checker[idx]:
                new_g1[idx] = 1
            else:
                new_g2[idx] = 1

        self.grid1 = new_g1
        self.grid2 = new_g2
        self.live_cells = new_live
        return self._get_live_counts_internal()

    def _get_live_counts_internal(self):
        livecells1 = sum(self.grid1)
        livecells2 = sum(self.grid2)
        livecells = livecells1 + livecells2

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
        coverage = livecells / (1.0 * total_area) * 100
        self.coverage = coverage

        territory1 = livecells1 / (1.0 * total_area) * 100
        territory2 = livecells2 / (1.0 * total_area) * 100
        self.territory1 = territory1
        self.territory2 = territory2

        return (self.generation, livecells, livecells1, livecells2, victory,
                coverage, territory1, territory2, self.running_avg_last3)

    def get_live_counts(self):
        t = self._get_live_counts_internal()
        return dict(
            generation=t[0], liveCells=t[1], liveCells1=t[2], liveCells2=t[3],
            victoryPct=t[4], coverage=t[5], territory1=t[6], territory2=t[7],
            last3=t[8],
        )

    def next_step(self):
        if self.running is False:
            return self.get_live_counts()
        elif self.halt and self.found_victor:
            self.running = False
            return self.get_live_counts()
        else:
            self.generation += 1
            self._next_generation_logic()
            self._update_moving_avg(self._get_live_counts_internal())
            return self.get_live_counts()
