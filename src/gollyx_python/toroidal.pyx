# cython: language_level=3

from operator import indexOf
import math
import json
import cython

cdef double EQUALTOL = 1e-8
cdef double SMOL = 1e-12

cdef class ToroidalGOL:
    cdef public object ic1, ic2
    cdef public int rows, columns
    cdef public list rule_b, rule_s
    cdef public int maxdim
    cdef public bint halt, periodic, running, found_victor
    cdef public int generation, who_won
    cdef public list running_avg_window, running_avg_last3
    cdef public list actual_state, actual_state1, actual_state2
    cdef public list redraw_list
    cdef int top_pointer, bottom_pointer
    cdef public int livecells, livecells1, livecells2
    cdef public double victory, coverage, territory1, territory2

    def __init__(
        self,
        s1,
        s2,
        int rows,
        int columns,
        list rule_b=None,
        list rule_s=None,
        int maxdim=280,
        bint halt=True,
        bint periodic=True,
        list b1=[],
        list b2=[],
        list c1=[],
        list c2=[],
    ):
        if isinstance(s1, str):
            s1 = json.loads(s1)
        if isinstance(s2, str):
            s2 = json.loads(s2)

        self.ic1 = s1
        self.ic2 = s2
        self.rows = rows
        self.columns = columns
        self.rule_b = rule_b or [3]
        self.rule_s = rule_s or [2, 3]
        self.maxdim = maxdim
        self.halt = halt
        self.periodic = periodic
        self.running = True
        self.generation = 0
        self.running_avg_window = [0.0] * self.maxdim
        self.running_avg_last3 = [0.0, 0.0, 0.0]
        self.found_victor = False
        self.actual_state = []
        self.actual_state1 = []
        self.actual_state2 = []
        self.prepare()

    cpdef get_live_cells(self):
        cdef list live1 = []
        cdef list row
        cdef int y, x
        for row in self.actual_state1:
            y = row[0]
            for x in row[1:]:
                live1.append((x, y))
        cdef list live2 = []
        for row in self.actual_state2:
            y = row[0]
            for x in row[1:]:
                live2.append((x, y))
        return live1, live2

    cpdef prepare(self):
        cdef list s1 = self.ic1
        cdef list s2 = self.ic2
        cdef dict s1row, s2row
        cdef str y_str
        cdef int y, yy, xx
        cdef list xs

        for s1row in s1:
            for y_str in s1row:
                yy = int(y_str)
                xs = s1row[y_str]
                for xx in xs:
                    self.actual_state = self.add_cell(xx, yy, self.actual_state)
                    self.actual_state1 = self.add_cell(xx, yy, self.actual_state1)

        for s2row in s2:
            for y_str in s2row:
                yy = int(y_str)
                xs = s2row[y_str]
                for xx in xs:
                    self.actual_state = self.add_cell(xx, yy, self.actual_state)
                    self.actual_state2 = self.add_cell(xx, yy, self.actual_state2)

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    cpdef update_moving_avg(self, dict livecounts):
        cdef int maxdim
        cdef double summ, running_avg, removed, tol
        cdef bint b1, b2, zerocells, z1, z2, z3

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

    cdef bint approx_equal(self, double a, double b, double tol):
        return (abs(b - a) / abs(a + SMOL)) < tol

    cpdef bint is_alive(self, int x, int y):
        cdef list row
        cdef int c

        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

        for row in self.actual_state:
            if row[0] == y:
                for c in row[1:]:
                    if c == x:
                        return True
        return False

    cdef int get_cell_color(self, int x, int y):
        cdef list row
        cdef int c

        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

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

    cdef void remove_cell(self, int x, int y, list state):
        cdef int i, j
        cdef list row

        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

        for i, row in enumerate(state):
            if row[0] == y:
                if len(row) == 2:
                    state[:] = state[:i] + state[i + 1 :]
                    return
                else:
                    j = indexOf(row, x)
                    state[i] = row[:j] + row[j + 1 :]
                    return

    cdef list add_cell(self, int x, int y, list state):
        cdef list new_state, new_row, row
        cdef bint added
        cdef int c, i

        if self.periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)

        if len(state) == 0:
            return [[y, x]]

        # Optimization: access first element if possible, but state is list of lists
        if y < state[0][0]:
            return [[y, x]] + state

        elif y > state[-1][0]:
            return state + [[y, x]]

        else:
            new_state = []
            added = False
            for row in state:
                if (not added) and (row[0] == y):
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
                    new_row = [y, x]
                    new_state.append(new_row)
                    added = True
                    new_state.append(row)
                else:
                    new_state.append(row)

            if added is False:
                raise Exception(f"Error adding cell ({x},{y}): new_state = {new_state}")

            return new_state

    cdef dict get_neighbors_from_alive(self, int x, int y, int i, list state, list possible_neighbors_list):
        cdef int neighbors = 0
        cdef int neighbors1 = 0
        cdef int neighbors2 = 0
        cdef int xm1, ym1, xp1, yp1
        cdef bint periodic = self.periodic
        cdef int im1, ip1, k, neighborcolor
        cdef list row_im1, row_i, row_ip1
        cdef int val

        xm1 = x - 1
        ym1 = y - 1
        xp1 = x + 1
        yp1 = y + 1

        if periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)
            xm1 = ((x-1) + self.columns)%(self.columns)
            ym1 = ((y-1) + self.rows)%(self.rows)
            xp1 = ((x+1) + self.columns)%(self.columns)
            yp1 = ((y+1) + self.rows)%(self.rows)

        im1 = i-1
        if im1 < 0:
            im1 = len(state)-1
        
        if im1 < len(state):
            row_im1 = state[im1]
            if row_im1[0] == ym1:
                for k in range(1, len(row_im1)):
                    val = row_im1[k]
                    if val >= xm1 or periodic:
                        if val == xm1:
                            possible_neighbors_list[0] = None
                            neighbors += 1
                            neighborcolor = self.get_cell_color(val, row_im1[0])
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1
                        if val == x:
                            possible_neighbors_list[1] = None
                            neighbors += 1
                            neighborcolor = self.get_cell_color(val, row_im1[0])
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1
                        if val == xp1:
                            possible_neighbors_list[2] = None
                            neighbors += 1
                            neighborcolor = self.get_cell_color(val, row_im1[0])
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1
                        if not periodic and val > xp1:
                            break

        row_i = state[i]
        for k in range(1, len(row_i)):
            val = row_i[k]
            if val >= xm1 or periodic:
                if val == xm1:
                    possible_neighbors_list[3] = None
                    neighbors += 1
                    neighborcolor = self.get_cell_color(val, row_i[0])
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1
                if val == xp1:
                    possible_neighbors_list[4] = None
                    neighbors += 1
                    neighborcolor = self.get_cell_color(val, row_i[0])
                    if neighborcolor == 1:
                        neighbors1 += 1
                    elif neighborcolor == 2:
                        neighbors2 += 1
                if not periodic and val > xp1:
                    break

        ip1 = i+1
        if ip1 >= len(state):
            ip1 = 0
        
        if ip1 < len(state):
            row_ip1 = state[ip1]
            if row_ip1[0] == yp1:
                for k in range(1, len(row_ip1)):
                    val = row_ip1[k]
                    if val >= xm1 or periodic:
                        if val == xm1:
                            possible_neighbors_list[5] = None
                            neighbors += 1
                            neighborcolor = self.get_cell_color(val, row_ip1[0])
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1
                        if val == x:
                            possible_neighbors_list[6] = None
                            neighbors += 1
                            neighborcolor = self.get_cell_color(val, row_ip1[0])
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1
                        if val == xp1:
                            possible_neighbors_list[7] = None
                            neighbors += 1
                            neighborcolor = self.get_cell_color(val, row_ip1[0])
                            if neighborcolor == 1:
                                neighbors1 += 1
                            elif neighborcolor == 2:
                                neighbors2 += 1
                        if not periodic and val > xp1:
                            break
        
        cdef int color = 0
        if neighbors1 > neighbors2:
            color = 1
        elif neighbors2 > neighbors1:
            color = 2
        elif x % 2 == y % 2:
            color = 1
        else:
            color = 2
        return {"neighbors": neighbors, "color": color}

    cdef int get_color_from_alive(self, int x, int y):
        cdef list state1 = self.actual_state1
        cdef list state2 = self.actual_state2
        cdef int color1 = 0
        cdef int color2 = 0
        cdef int xm1, ym1, xp1, yp1
        cdef bint periodic = self.periodic
        cdef int i, j, yy, xx, color

        xm1 = x - 1
        ym1 = y - 1
        xp1 = x + 1
        yp1 = y + 1

        if periodic:
            x = (x + self.columns)%(self.columns)
            y = (y + self.rows)%(self.rows)
            xm1 = ((x-1) + self.columns)%(self.columns)
            ym1 = ((y-1) + self.rows)%(self.rows)
            xp1 = ((x+1) + self.columns)%(self.columns)
            yp1 = ((y+1) + self.rows)%(self.rows)

        for i in range(len(state1)):
            yy = state1[i][0]
            if yy == ym1:
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            color1 += 1
                        elif xx == x:
                            color1 += 1
                        elif xx == xp1:
                            color1 += 1
                    if not periodic and xx >= xp1:
                        break
            elif yy == y:
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            color1 += 1
                        elif xx == xp1:
                            color1 += 1
                    if not periodic and xx >= xp1:
                        break
            elif yy == yp1:
                for j in range(1, len(state1[i])):
                    xx = state1[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            color1 += 1
                        elif xx == x:
                            color1 += 1
                        elif xx == xp1:
                            color1 += 1
                    if not periodic and xx >= xp1:
                        break

        for i in range(len(state2)):
            yy = state2[i][0]
            if yy == ym1:
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            color2 += 1
                        elif xx == x:
                            color2 += 1
                        elif xx == xp1:
                            color2 += 1
                    if not periodic and xx >= xp1:
                        break
            elif yy == y:
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            color2 += 1
                        elif xx == xp1:
                            color2 += 1
                    if not periodic and xx >= xp1:
                        break
            elif yy == yp1:
                for j in range(1, len(state2[i])):
                    xx = state2[i][j]
                    if xx >= xm1 or periodic:
                        if xx == xm1:
                            color2 += 1
                        elif xx == x:
                            color2 += 1
                        elif xx == xp1:
                            color2 += 1
                    if not periodic and xx >= xp1:
                        break

        if color1 > color2:
            return 1
        elif color1 < color2:
            return 2
        elif x % 2 == y % 2:
            color = 1
        else:
            color = 2
        return color

    cdef dict _next_generation_logic(self):
        cdef dict all_dead_neighbors = {}
        cdef list new_state = []
        cdef list new_state1 = []
        cdef list new_state2 = []
        cdef list row
        cdef int i, j, x, y, xm1, ym1, xp1, yp1, t1, t2, neighbors, color
        cdef list dead_neighbors, dead_neighbor
        cdef str key
        cdef dict result

        self.redraw_list = []

        for i in range(len(self.actual_state)):
            self.top_pointer = 1
            self.bottom_pointer = 1
            row = self.actual_state[i]
            y = row[0]
            
            for j in range(1, len(row)):
                x = row[j]
                
                xm1 = x - 1
                ym1 = y - 1
                xp1 = x + 1
                yp1 = y + 1

                if self.periodic:
                    x = (x + self.columns)%(self.columns)
                    y = (y + self.rows)%(self.rows)
                    xm1 = ((x-1) + self.columns)%(self.columns)
                    ym1 = ((y-1) + self.rows)%(self.rows)
                    xp1 = ((x+1) + self.columns)%(self.columns)
                    yp1 = ((y+1) + self.rows)%(self.rows)

                dead_neighbors = [
                    [xm1, ym1, 1], [x,   ym1, 1], [xp1, ym1, 1],
                    [xm1, y,   1], [xp1, y,   1],
                    [xm1, yp1, 1], [x,   yp1, 1], [xp1, yp1, 1],
                ]

                result = self.get_neighbors_from_alive(
                    x, y, i, self.actual_state, dead_neighbors
                )
                neighbors = result["neighbors"]
                color = result["color"]

                for dead_neighbor in dead_neighbors:
                    if dead_neighbor is not None:
                        # xx = dead_neighbor[0]
                        # yy = dead_neighbor[1]
                        # key = str(xx) + "," + str(yy)
                        key = f"{dead_neighbor[0]},{dead_neighbor[1]}"
                        if key not in all_dead_neighbors:
                            all_dead_neighbors[key] = 1
                        else:
                            all_dead_neighbors[key] += 1

                if neighbors in self.rule_s:
                    new_state = self.add_cell(x, y, new_state)
                    if color == 1:
                        new_state1 = self.add_cell(x, y, new_state1)
                    elif color == 2:
                        new_state2 = self.add_cell(x, y, new_state2)
                    self.redraw_list.append([x, y, 2])
                else:
                    self.redraw_list.append([x, y, 0])

        for key in all_dead_neighbors:
            if all_dead_neighbors[key] in self.rule_b:
                # key = key.split(",")
                # t1 = int(key[0])
                # t2 = int(key[1])
                t1, t2 = map(int, key.split(","))
                
                color = self.get_color_from_alive(t1, t2)
                new_state = self.add_cell(t1, t2, new_state)
                if color == 1:
                    new_state1 = self.add_cell(t1, t2, new_state1)
                elif color == 2:
                    new_state2 = self.add_cell(t1, t2, new_state2)
                self.redraw_list.append([t1, t2, 1])

        self.actual_state = new_state
        self.actual_state1 = new_state1
        self.actual_state2 = new_state2
        return self.get_live_counts()

    cpdef dict get_live_counts(self):
        cdef int livecells = 0
        cdef int livecells1 = 0
        cdef int livecells2 = 0
        cdef int i, j, row_len

        # Inlining _count_live_cells for actual_state
        for i in range(len(self.actual_state)):
            if (self.actual_state[i][0] >= 0) and (self.actual_state[i][0] < self.rows):
                row_len = len(self.actual_state[i])
                for j in range(1, row_len):
                    if (self.actual_state[i][j] >= 0) and (self.actual_state[i][j] < self.columns):
                        livecells += 1
        
        # Inlining _count_live_cells for actual_state1
        for i in range(len(self.actual_state1)):
            if (self.actual_state1[i][0] >= 0) and (self.actual_state1[i][0] < self.rows):
                row_len = len(self.actual_state1[i])
                for j in range(1, row_len):
                    if (self.actual_state1[i][j] >= 0) and (self.actual_state1[i][j] < self.columns):
                        livecells1 += 1
        
        # Inlining _count_live_cells for actual_state2
        for i in range(len(self.actual_state2)):
            if (self.actual_state2[i][0] >= 0) and (self.actual_state2[i][0] < self.rows):
                row_len = len(self.actual_state2[i])
                for j in range(1, row_len):
                    if (self.actual_state2[i][j] >= 0) and (self.actual_state2[i][j] < self.columns):
                        livecells2 += 1

        self.livecells = livecells
        self.livecells1 = livecells1
        self.livecells2 = livecells2

        cdef double victory = 0.0
        if livecells1 > livecells2:
            victory = livecells1 / (1.0 * livecells1 + livecells2 + SMOL)
        else:
            victory = livecells2 / (1.0 * livecells1 + livecells2 + SMOL)
        victory = victory * 100
        self.victory = victory

        cdef double total_area = self.columns * self.rows
        cdef double coverage = livecells / (1.0 * total_area)
        coverage = coverage * 100
        self.coverage = coverage

        cdef double territory1 = livecells1 / (1.0 * total_area)
        territory1 = territory1 * 100
        cdef double territory2 = livecells2 / (1.0 * total_area)
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

    cpdef dict next_step(self):
        cdef dict live_counts
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
