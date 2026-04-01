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

        self.alive1 = set()
        self.alive2 = set()

        self.prepare()

    def get_live_cells(self):
        return list(self.alive1), list(self.alive2)

    def prepare(self):
        s1 = self.ic1
        s2 = self.ic2
        columns = self.columns
        rows = self.rows

        for s1row in s1:
            for y in s1row:
                yy = int(y) % rows
                for xx in s1row[y]:
                    self.alive1.add((xx % columns, yy))

        for s2row in s2:
            for y in s2row:
                yy = int(y) % rows
                for xx in s2row[y]:
                    self.alive2.add((xx % columns, yy))

        livecounts = self._get_live_counts()
        self._update_moving_avg(livecounts)

    def _update_moving_avg(self, livecounts):
        if self.found_victor:
            return
        maxdim = self.maxdim
        gen = self.generation
        if gen < maxdim:
            self.running_avg_window[gen] = livecounts[4]  # victoryPct
        else:
            w = self.running_avg_window
            w.pop(0)
            w.append(livecounts[4])
            running_avg = sum(w) / (1.0 * len(w))

            removed = self.running_avg_last3[0]
            self.running_avg_last3 = [self.running_avg_last3[1], self.running_avg_last3[2], running_avg]

            tol = EQUALTOL
            smol = SMOL
            # inline approx_equal
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
        alive1 = self.alive1
        alive2 = self.alive2
        columns = self.columns
        rows = self.rows

        # Single dict: key -> [total_count, c1_count]
        counts = {}
        counts_get = counts.get

        for x, y in alive1:
            xm1 = (x - 1) % columns
            xp1 = (x + 1) % columns
            ym1 = (y - 1) % rows
            yp1 = (y + 1) % rows

            k = (xm1, ym1); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]
            k = (x, ym1); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]
            k = (xp1, ym1); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]
            k = (xm1, y); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]
            k = (xp1, y); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]
            k = (xm1, yp1); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]
            k = (x, yp1); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]
            k = (xp1, yp1); v = counts_get(k)
            if v is not None: v[0] += 1; v[1] += 1
            else: counts[k] = [1, 1]

        for x, y in alive2:
            xm1 = (x - 1) % columns
            xp1 = (x + 1) % columns
            ym1 = (y - 1) % rows
            yp1 = (y + 1) % rows

            k = (xm1, ym1); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]
            k = (x, ym1); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]
            k = (xp1, ym1); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]
            k = (xm1, y); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]
            k = (xp1, y); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]
            k = (xm1, yp1); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]
            k = (x, yp1); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]
            k = (xp1, yp1); v = counts_get(k)
            if v is not None: v[0] += 1
            else: counts[k] = [1, 0]

        new_alive1 = set()
        new_alive2 = set()
        na1_add = new_alive1.add
        na2_add = new_alive2.add

        rule_s = self.rule_s
        rule_b = self.rule_b
        a1_contains = alive1.__contains__
        a2_contains = alive2.__contains__

        for key, val in counts.items():
            total = val[0]
            is_alive = a1_contains(key) or a2_contains(key)

            if is_alive:
                if total not in rule_s:
                    continue
            else:
                if total not in rule_b:
                    continue

            c1 = val[1]
            c2 = total - c1
            if c1 > c2:
                na1_add(key)
            elif c2 > c1:
                na2_add(key)
            elif key[0] % 2 == key[1] % 2:
                na1_add(key)
            else:
                na2_add(key)

        self.alive1 = new_alive1
        self.alive2 = new_alive2
        return self._get_live_counts()

    def _get_live_counts(self):
        livecells1 = len(self.alive1)
        livecells2 = len(self.alive2)
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
        t = self._get_live_counts()
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
            live_counts = self._next_generation_logic()
            self._update_moving_avg(live_counts)
            return self.get_live_counts()
