import json
from array import array

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
        self.running_avg_idx = 0  # circular buffer write index
        self.running_avg_last3 = [0, 0, 0]
        self.running_avg_sum = 0.0
        self.found_victor = False

        sz = rows * columns
        self.sz = sz
        self.total_area = float(sz)
        # Alive buffer: ab[idx] = 1 if cell is alive (either team)
        self.alive_buf = bytearray(sz)

        # Flat neighbor table: 8 neighbors per cell stored contiguously
        nt = array('l', [0] * (sz * 8))
        for y in range(rows):
            for x in range(columns):
                base = (y * columns + x) * 8
                xm1 = (x - 1) % columns
                xp1 = (x + 1) % columns
                ym1 = (y - 1) % rows
                yp1 = (y + 1) % rows
                nt[base]     = ym1 * columns + xm1
                nt[base + 1] = ym1 * columns + x
                nt[base + 2] = ym1 * columns + xp1
                nt[base + 3] = y * columns + xm1
                nt[base + 4] = y * columns + xp1
                nt[base + 5] = yp1 * columns + xm1
                nt[base + 6] = yp1 * columns + x
                nt[base + 7] = yp1 * columns + xp1
        self._nt = nt

        self._checker = bytearray(sz)
        for y in range(rows):
            for x in range(columns):
                if x % 2 == y % 2:
                    self._checker[y * columns + x] = 1

        # Combined buffer: encodes (total << 4) | c1 in single int
        # Max total = 8, max c1 = 8, so fits in one int
        # Increment by 17 (=16+1) for team1 neighbor, 16 for team2 neighbor
        self._combo_buf = array('l', [0] * sz)
        self._dirty = array('l', [0] * (sz * 9))

        self.prepare()

    def prepare(self):
        s1 = self.ic1
        s2 = self.ic2
        columns = self.columns
        rows = self.rows
        ab = self.alive_buf
        live_c1 = []
        live_c2 = []

        for s1row in s1:
            for y_str in s1row:
                y = int(y_str) % rows
                for x in s1row[y_str]:
                    x = x % columns
                    idx = y * columns + x
                    ab[idx] = 1
                    live_c1.append(idx)

        for s2row in s2:
            for y_str in s2row:
                y = int(y_str) % rows
                for x in s2row[y_str]:
                    x = x % columns
                    idx = y * columns + x
                    ab[idx] = 1
                    live_c2.append(idx)

        self.live_c1 = live_c1
        self.live_c2 = live_c2
        self.livecells1 = len(live_c1)
        self.livecells2 = len(live_c2)
        self.livecells = self.livecells1 + self.livecells2

        # Initialize victory detection
        lc1 = self.livecells1
        lc2 = self.livecells2
        if lc1 > lc2:
            vp = lc1 / (1.0 * lc1 + lc2 + SMOL) * 100
        else:
            vp = lc2 / (1.0 * lc1 + lc2 + SMOL) * 100
        self.running_avg_window[0] = vp
        self.running_avg_sum = vp

    def get_live_cells(self):
        columns = self.columns
        live1 = [(idx % columns, idx // columns) for idx in self.live_c1]
        live2 = [(idx % columns, idx // columns) for idx in self.live_c2]
        return live1, live2

    def _next_generation_logic(self):
        ab = self.alive_buf
        nt = self._nt
        checker = self._checker
        rule_s = self.rule_s
        rule_b = self.rule_b
        combo_buf = self._combo_buf
        dirty = self._dirty
        dirty_count = 0
        INC_C1 = 17  # (1 << 4) + 1
        INC_C2 = 16  # (1 << 4)

        # Scatter from team1 cells
        for idx in self.live_c1:
            base = idx * 8
            n0 = nt[base]; n1 = nt[base+1]; n2 = nt[base+2]; n3 = nt[base+3]
            n4 = nt[base+4]; n5 = nt[base+5]; n6 = nt[base+6]; n7 = nt[base+7]

            if combo_buf[n0] == 0: dirty[dirty_count] = n0; dirty_count += 1
            combo_buf[n0] += INC_C1
            if combo_buf[n1] == 0: dirty[dirty_count] = n1; dirty_count += 1
            combo_buf[n1] += INC_C1
            if combo_buf[n2] == 0: dirty[dirty_count] = n2; dirty_count += 1
            combo_buf[n2] += INC_C1
            if combo_buf[n3] == 0: dirty[dirty_count] = n3; dirty_count += 1
            combo_buf[n3] += INC_C1
            if combo_buf[n4] == 0: dirty[dirty_count] = n4; dirty_count += 1
            combo_buf[n4] += INC_C1
            if combo_buf[n5] == 0: dirty[dirty_count] = n5; dirty_count += 1
            combo_buf[n5] += INC_C1
            if combo_buf[n6] == 0: dirty[dirty_count] = n6; dirty_count += 1
            combo_buf[n6] += INC_C1
            if combo_buf[n7] == 0: dirty[dirty_count] = n7; dirty_count += 1
            combo_buf[n7] += INC_C1

        # Scatter from team2 cells
        for idx in self.live_c2:
            base = idx * 8
            n0 = nt[base]; n1 = nt[base+1]; n2 = nt[base+2]; n3 = nt[base+3]
            n4 = nt[base+4]; n5 = nt[base+5]; n6 = nt[base+6]; n7 = nt[base+7]

            if combo_buf[n0] == 0: dirty[dirty_count] = n0; dirty_count += 1
            combo_buf[n0] += INC_C2
            if combo_buf[n1] == 0: dirty[dirty_count] = n1; dirty_count += 1
            combo_buf[n1] += INC_C2
            if combo_buf[n2] == 0: dirty[dirty_count] = n2; dirty_count += 1
            combo_buf[n2] += INC_C2
            if combo_buf[n3] == 0: dirty[dirty_count] = n3; dirty_count += 1
            combo_buf[n3] += INC_C2
            if combo_buf[n4] == 0: dirty[dirty_count] = n4; dirty_count += 1
            combo_buf[n4] += INC_C2
            if combo_buf[n5] == 0: dirty[dirty_count] = n5; dirty_count += 1
            combo_buf[n5] += INC_C2
            if combo_buf[n6] == 0: dirty[dirty_count] = n6; dirty_count += 1
            combo_buf[n6] += INC_C2
            if combo_buf[n7] == 0: dirty[dirty_count] = n7; dirty_count += 1
            combo_buf[n7] += INC_C2

        # Process dirty cells
        new_c1 = []
        new_c1_append = new_c1.append
        new_c2 = []
        new_c2_append = new_c2.append

        for i in range(dirty_count):
            idx = dirty[i]
            combo = combo_buf[idx]
            combo_buf[idx] = 0
            total = combo >> 4
            c1 = combo & 15

            if ab[idx]:
                if total not in rule_s:
                    continue
            else:
                if total not in rule_b:
                    continue

            c2 = total - c1
            if c1 > c2:
                new_c1_append(idx)
            elif c2 > c1:
                new_c2_append(idx)
            elif checker[idx]:
                new_c1_append(idx)
            else:
                new_c2_append(idx)

        # Update alive buffer
        for idx in self.live_c1:
            ab[idx] = 0
        for idx in self.live_c2:
            ab[idx] = 0
        for idx in new_c1:
            ab[idx] = 1
        for idx in new_c2:
            ab[idx] = 1
        self.live_c1 = new_c1
        self.live_c2 = new_c2
        lc1 = len(new_c1)
        lc2 = len(new_c2)
        self.livecells1 = lc1
        self.livecells2 = lc2
        self.livecells = lc1 + lc2

        # Victory detection (skip entirely once found)
        if not self.found_victor:
            if lc1 > lc2:
                victory = lc1 / (1.0 * lc1 + lc2 + SMOL) * 100
            else:
                victory = lc2 / (1.0 * lc1 + lc2 + SMOL) * 100
            gen = self.generation
            maxdim = self.maxdim
            if gen < maxdim:
                self.running_avg_window[gen] = victory
                self.running_avg_sum += victory
            else:
                w = self.running_avg_window
                widx = self.running_avg_idx
                old_val = w[widx]
                w[widx] = victory
                self.running_avg_idx = (widx + 1) % maxdim
                self.running_avg_sum += victory - old_val
                running_avg = self.running_avg_sum / (1.0 * maxdim)

                removed = self.running_avg_last3[0]
                self.running_avg_last3 = [self.running_avg_last3[1], self.running_avg_last3[2], running_avg]

                tol = EQUALTOL
                smol = SMOL
                denom = max(abs(removed), smol)
                if not ((abs(removed) / denom) < tol):
                    ra = self.running_avg_last3
                    d01 = abs(ra[0] - ra[1])
                    mx01 = max(abs(ra[0]), abs(ra[1]), smol)
                    b1_ = (d01 / mx01) < tol
                    d12 = abs(ra[1] - ra[2])
                    mx12 = max(abs(ra[1]), abs(ra[2]), smol)
                    b2_ = (d12 / mx12) < tol

                    zerocells = lc1 == 0 or lc2 == 0

                    if (b1_ and b2_) or zerocells:
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

    def get_live_counts(self):
        lc1 = self.livecells1
        lc2 = self.livecells2
        livecells = self.livecells

        if lc1 > lc2:
            victory = lc1 / (1.0 * lc1 + lc2 + SMOL) * 100
        else:
            victory = lc2 / (1.0 * lc1 + lc2 + SMOL) * 100

        total_area = self.total_area
        return dict(
            generation=self.generation,
            liveCells=livecells,
            liveCells1=lc1,
            liveCells2=lc2,
            victoryPct=victory,
            coverage=livecells / (1.0 * total_area) * 100,
            territory1=lc1 / (1.0 * total_area) * 100,
            territory2=lc2 / (1.0 * total_area) * 100,
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
            self._next_generation_logic()
            return self.get_live_counts()
