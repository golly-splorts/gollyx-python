# cython: language_level=3

from operator import indexOf
import math
import json
import cython

# Default value for dimension (in time) of time-average window
cdef int MAXDIM = 280

cdef class StarGOL:
    cdef public int generation
    cdef public int columns, rows, width, height
    cdef public int livecells
    cdef public list livecellscolors
    cdef public double victory, coverage
    cdef public int who_won
    cdef public bint found_victor, running, periodic, halt
    cdef public list running_avg_window, running_avg_last3
    cdef public double tol_zero, tol_stable
    
    cdef public list rule_b, rule_s
    cdef public int rule_c, maxdim
    
    cdef public list actual_state
    cdef public list actual_state_colors
    cdef public list dead_wait_n
    cdef public list dead_wait_colors_n

    def __init__(
        self,
        s1=[],
        s2=[],
        int rows=0,
        int columns=0,
        list rule_b=None,
        list rule_s=None,
        int rule_c=4,
        bint periodic=True,
        int maxdim=MAXDIM,
        list b1=[],
        list b2=[],
        list c1=[],
        list c2=[],
        **kwargs,
    ):
        if isinstance(s1, str):
            s1 = json.loads(s1)
        if isinstance(s2, str):
            s2 = json.loads(s2)

        self.rows = rows
        self.columns = columns
        self.width = columns
        self.height = rows

        self.rule_b = rule_b or [3]
        self.rule_s = rule_s or [2, 3]
        self.rule_c = rule_c

        self.maxdim = maxdim
        self.halt = True
        self.periodic = periodic

        # Tolerances
        self.tol_zero = kwargs.get("tol_zero", 1e-8)
        self.tol_stable = kwargs.get("tol_stable", 1e-6)

        self.running_avg_window = []
        self.running_avg_last3 = [0.0, 0.0, 0.0]
        self.livecellscolors = []
        
        self.set_pattern(s1, s2, b1, b2, c1, c2)

    cpdef set_pattern(self, pattern_color1, pattern_color2, list pattern_b1=[], list pattern_b2=[], list pattern_c1=[], list pattern_c2=[]):
        """similar to setInitialState in starlife.py"""
        cdef int i, level_index, color, y, yy, xx
        cdef list dead_wait_color_j, xs
        cdef dict s1row, s2row, row
        cdef str y_str
        cdef bint is_occupied
        cdef tuple pattern_data
        
        # Reset state for fresh run
        self.actual_state = []
        self.actual_state_colors = [set(), set(), set()]
        self.dead_wait_n = []
        self.dead_wait_colors_n = []
        
        for i in range(self.rule_c - 2):
            self.dead_wait_n.append([])
            dead_wait_color_j = [set(), set(), set()]
            self.dead_wait_colors_n.append(dead_wait_color_j)
            
        self.generation = 0
        self.running_avg_window = [0.0] * self.maxdim
        self.running_avg_last3 = [0.0, 0.0, 0.0]
        self.found_victor = False
        self.running = True

        # Process alive cells
        for s1row in pattern_color1:
            for y_str in s1row:
                yy = int(y_str)
                xs = s1row[y_str]
                for xx in xs:
                    self.add_alive_cell(xx, yy, 1)
        for s2row in pattern_color2:
            for y_str in s2row:
                yy = int(y_str)
                xs = s2row[y_str]
                for xx in xs:
                    self.add_alive_cell(xx, yy, 2)

        # Process dead-but-waiting states
        dead_wait_patterns = [
            (pattern_b1, 1, 0),
            (pattern_b2, 2, 0),
            (pattern_c1, 1, 1),
            (pattern_c2, 2, 1),
        ]

        for pattern_data in dead_wait_patterns:
            # (pattern_data, color, level_index)
            # Tuple unpacking manually or typed
            p_data = pattern_data[0]
            color = pattern_data[1]
            level_index = pattern_data[2]
            
            for row in p_data:
                for y_str in row:
                    yy = int(y_str)
                    xs = row[y_str]
                    for xx in xs:
                        # Check if cell is already occupied at a higher-priority state
                        is_occupied = False
                        if self.is_alive(xx, yy):
                            is_occupied = True
                        else:
                            # Check all dead-wait levels up to (but not including) the current one
                            for i in range(level_index):
                                if self.is_dead_wait_at_level(xx, yy, i):
                                    is_occupied = True
                                    break
                        
                        if not is_occupied:
                            # target_state = self.dead_wait_n[level_index]
                            # target_color_set = self.dead_wait_colors_n[level_index]
                            
                            res = self.add_cell_to_custom_state(
                                xx, yy, 
                                self.dead_wait_n[level_index], 
                                self.dead_wait_colors_n[level_index], 
                                color
                            )
                            self.dead_wait_n[level_index] = res[0]
                            self.dead_wait_colors_n[level_index] = res[1]

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    cpdef bint check_for_victor(self):
        if self.found_victor:
            return True
        else:
            return False

    cdef bint is_dead_wait_at_level(self, int x, int y, int level_index):
        cdef str rep = f"({x},{y})"
        cdef int color0
        cdef list colors_n = self.dead_wait_colors_n[level_index]
        for color0 in range(3):
            if rep in colors_n[color0]:
                return True
        return False

    cpdef update_moving_avg(self, dict livecounts=None):
        cdef int maxdim
        cdef double rootsum, summ, running_avg, removed, tol_zero, tol_stable
        cdef bint b1, b2, victory_by_stability, victory_by_shutout
        cdef int i, zero_score_counter, threshold

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
                    # We are here because we have a nonzero running average (game is going), and no victor
                    # Check if average has become stable
                    b1 = self.approx_equal(
                        self.running_avg_last3[0], self.running_avg_last3[1], tol_stable
                    )
                    b2 = self.approx_equal(
                        self.running_avg_last3[1], self.running_avg_last3[2], tol_stable
                    )
                    victory_by_stability = (b1 and b2) and (livecounts['liveCells'] > 0)

                    if victory_by_stability:
                        # Someone won due to simulation becoming stable
                        self.found_victor = True
                        if livecounts["liveCellsColors"][0] > livecounts["liveCellsColors"][1]:
                            self.who_won = 1
                        elif livecounts["liveCellsColors"][0] < livecounts["liveCellsColors"][1]:
                            self.who_won = 2
                        else:
                            # Tie
                            self.who_won = -1

            # The second way for a victor to be declared,
            # is to have all other teams get shut out.
            # But if gen < maxDim, this game is invalid.
            victory_by_shutout = False

            # Hard-coded rules format
            zero_score_counter = 0
            threshold = 1
            for i in range(2):
                if livecounts["liveCellsColors"][i] == 0:
                    zero_score_counter += 1
            if zero_score_counter >= threshold:
                victory_by_shutout = True

            if victory_by_shutout:
                # Someone won by shutting out the other team
                self.found_victor = True
                if self.generation < maxdim:
                    self.who_won = -1
                else:
                    if livecounts["liveCellsColors"][0] > livecounts["liveCellsColors"][1]:
                        self.who_won = 1
                    elif livecounts["liveCellsColors"][0] < livecounts["liveCellsColors"][1]:
                        self.who_won = 2
                    else:
                        # Tie
                        self.who_won = -1

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

    cpdef dict next_generation(self):
        return self.next_step()

    cdef dict _next_generation_logic(self):
        cdef dict all_dead_neighbors = {}
        cdef list new_state = []
        cdef list new_state_colors = [set(), set(), set()]
        cdef list new_dead_wait_n = []
        cdef list new_dead_wait_colors_n = []
        cdef list new_dead_wait_colors_j
        cdef int i, j, x, y, xm1, ym1, xp1, yp1, t1, t2, color, neighbors
        cdef list dead_neighbors, dead_neighbor
        cdef str key
        cdef dict result
        cdef tuple res_tuple
        cdef int cmax_ix, c, cm1
        cdef list row

        for i in range(self.rule_c - 2):
            new_dead_wait_n.append([])
            new_dead_wait_colors_j = [set(), set(), set()]
            new_dead_wait_colors_n.append(new_dead_wait_colors_j)
        
        # -----
        # SURVIVE step

        for i in range(len(self.actual_state)):
            row = self.actual_state[i]
            y = row[0]
            for j in range(1, len(row)):
                x = row[j]
                
                xm1 = x - 1
                ym1 = y - 1
                xp1 = x + 1
                yp1 = y + 1

                if self.periodic:
                    xm1 = self.periodic_normalize_x(x - 1)
                    ym1 = self.periodic_normalize_y(y - 1)
                    xp1 = self.periodic_normalize_x(x + 1)
                    yp1 = self.periodic_normalize_y(y + 1)
                    x = self.periodic_normalize_x(x)
                    y = self.periodic_normalize_y(y)

                dead_neighbors = [
                    [xm1, ym1, 1], [x, ym1, 1], [xp1, ym1, 1],
                    [xm1, y, 1], [xp1, y, 1],
                    [xm1, yp1, 1], [x, yp1, 1], [xp1, yp1, 1],
                ]

                result, dead_neighbors = self.get_neighbors_from_alive(x, y, dead_neighbors)
                neighbors = result["neighbors"]
                color = result["color"]

                for dead_neighbor in dead_neighbors:
                    if dead_neighbor is not None:
                        # xx, yy = dead_neighbor[0], dead_neighbor[1]
                        # key = str(xx) + "," + str(yy)
                        # key = f"{dead_neighbor[0]},{dead_neighbor[1]}"
                        # Explicit typing for logic
                        if not self.is_dead_wait(dead_neighbor[0], dead_neighbor[1]):
                            key = f"{dead_neighbor[0]},{dead_neighbor[1]}"
                            if key not in all_dead_neighbors:
                                all_dead_neighbors[key] = 1
                            else:
                                all_dead_neighbors[key] += 1

                if neighbors in self.rule_s:
                    res_tuple = self.add_cell_to_custom_state(
                        x, y, new_state, new_state_colors, color
                    )
                    new_state = res_tuple[0]
                    new_state_colors = res_tuple[1]
                else:
                    res_tuple = self.add_cell_to_custom_state(
                        x, y, new_dead_wait_n[0], new_dead_wait_colors_n[0], color
                    )
                    new_dead_wait_n[0] = res_tuple[0]
                    new_dead_wait_colors_n[0] = res_tuple[1]
        # -----

        # -----
        # BIRTH step
        for key in all_dead_neighbors:
            if all_dead_neighbors[key] in self.rule_b:
                t1, t2 = map(int, key.split(","))
                color = self.get_color_from_alive(t1, t2)
                res_tuple = self.add_cell_to_custom_state(
                    t1, t2, new_state, new_state_colors, color
                )
                new_state = res_tuple[0]
                new_state_colors = res_tuple[1]
        # -----

        # -----
        # DEAD WAIT CYCLING step
        cmax_ix = self.rule_c - 2 - 1
        for c in range(cmax_ix, -1, -1):
            if c > 0:
                cm1 = c - 1
                new_dead_wait_n[c] = self.dead_wait_n[cm1]
                new_dead_wait_colors_n[c] = [s.copy() for s in self.dead_wait_colors_n[cm1]]
        # -----

        self.actual_state = new_state
        self.actual_state_colors = new_state_colors
        self.dead_wait_n = new_dead_wait_n
        self.dead_wait_colors_n = new_dead_wait_colors_n

        return self.get_live_counts()

    cpdef tuple get_live_cells(self):
        """
        Return the coordinates of all live cells for each color.
        """
        cdef list live_cells_color1 = []
        cdef list live_cells_color2 = []
        cdef list live_cells_color3 = []
        cdef str rep, x_str, y_str
        
        for rep in self.actual_state_colors[0]:
            x_str, y_str = rep.strip('()').split(',')
            live_cells_color1.append((int(x_str), int(y_str)))
        for rep in self.actual_state_colors[1]:
            x_str, y_str = rep.strip('()').split(',')
            live_cells_color2.append((int(x_str), int(y_str)))
        for rep in self.actual_state_colors[2]:
            x_str, y_str = rep.strip('()').split(',')
            live_cells_color3.append((int(x_str), int(y_str)))
        return live_cells_color1, live_cells_color2, live_cells_color3

    cdef int _get_state_count(self, list state):
        cdef int count = 0
        cdef list row
        for row in state:
            count += len(row) - 1
        return count

    cpdef dict get_live_counts(self):
        cdef int livecells
        cdef list livecells_colors
        cdef double total_area, coverage
        
        livecells = self._get_state_count(self.actual_state)
        livecells_colors = [len(s) for s in self.actual_state_colors]
        
        if sum(livecells_colors) != livecells:
            err = f"Error: get_live_counts inconsistent: alive={livecells}, sum_colors={sum(livecells_colors)}"
            raise Exception(err)

        total_area = self.columns * self.rows
        if total_area > 0:
            coverage = (livecells / (1.0 * total_area)) * 100
        else:
            coverage = 0
        self.coverage = coverage

        return dict(
            generation=self.generation,
            liveCells=livecells,
            liveCells1=livecells_colors[0],
            liveCells2=livecells_colors[1],
            liveCellsColors=livecells_colors,
            coverage=coverage,
            last3=self.running_avg_last3,
        )

    cdef tuple get_neighbors_from_alive(self, int x, int y, list possible_neighbors_list):
        cdef list neighbors_colors = [0, 0, 0]
        cdef int i
        cdef tuple res
        cdef int neighbors, neighbors_norefs, color
        cdef list neighbors_dw = [0, 0]
        cdef int max_neighbor, num_equal_max
        cdef int max_neighbor_dw, num_equal_max_dw
        
        for i in range(3):
            res = self.get_color_counts_from_possible_neighbors(x, y, i+1, possible_neighbors_list)
            neighbors_colors[i] = res[0]
            possible_neighbors_list = res[1]
            
        neighbors = sum(neighbors_colors)
        neighbors_norefs = neighbors_colors[0] + neighbors_colors[1]

        for i in range(2):
            neighbors_dw[i] = self.get_color_counts_from_dead_wait(x, y, i+1)

        color = 0
        if neighbors > 0:
            if neighbors_norefs > 0:
                max_neighbor = max(neighbors_colors[0], neighbors_colors[1])
                num_equal_max = (neighbors_colors[0] == max_neighbor) + (neighbors_colors[1] == max_neighbor)
                
                if num_equal_max == 1:
                    color = 1 if neighbors_colors[0] > neighbors_colors[1] else 2
                else: # Tie
                    max_neighbor_dw = max(neighbors_colors[0]+neighbors_dw[0], neighbors_colors[1]+neighbors_dw[1])
                    num_equal_max_dw = (neighbors_colors[0]+neighbors_dw[0] == max_neighbor_dw) + (neighbors_colors[1]+neighbors_dw[1] == max_neighbor_dw)
                    if num_equal_max_dw == 1:
                        color = 1 if (neighbors_colors[0]+neighbors_dw[0]) > (neighbors_colors[1]+neighbors_dw[1]) else 2
                    else:
                        color = -1 # Still a tie, keep original color
            else:
                color = -1 # Only ref neighbors, keep original color
        else:
            color = -1 # No neighbors, keep original color

        if color < 0:
            color = self.get_cell_color(x, y)

        return {"neighbors": neighbors, "color": color}, possible_neighbors_list

    cdef int get_color_from_alive(self, int x, int y):
        cdef list neighbors_colors = [0, 0, 0]
        cdef int i, neighbors, neighbors_norefs, color, max_neighbor, num_equal_max
        
        for i in range(3):
            neighbors_colors[i] = self.get_color_counts_from_alive(x, y, i+1)
        neighbors = sum(neighbors_colors)
        neighbors_norefs = neighbors_colors[0] + neighbors_colors[1]

        color = 0
        if neighbors > 0:
            if neighbors_norefs > 0:
                max_neighbor = max(neighbors_colors[0], neighbors_colors[1])
                num_equal_max = (neighbors_colors[0] == max_neighbor) + (neighbors_colors[1] == max_neighbor)
                if num_equal_max == 1:
                    color = 1 if neighbors_colors[0] > neighbors_colors[1] else 2
                else:
                    color = 3 # Tie becomes a referee
            else:
                color = 3 # Only referee neighbors
        return color

    cdef int get_color_counts_from_dead_wait(self, int x, int y, int color):
        cdef int color0 = color - 1
        cdef int dead_wait_count = 0
        cdef int c, iy, ix, xx, yy
        cdef set points
        
        for c in range(self.rule_c-2):
            points = self.dead_wait_colors_n[c][color0]
            for iy in [-1, 0, 1]:
                for ix in [-1, 0, 1]:
                    if ix == 0 and iy == 0: continue
                    xx, yy = self.periodic_normalize_x(x + ix), self.periodic_normalize_y(y + iy)
                    if f"({xx},{yy})" in points:
                        dead_wait_count += 1
        return dead_wait_count

    cdef int get_color_counts_from_alive(self, int x, int y, int color):
        cdef int color0 = color - 1
        cdef int alive_count = 0
        cdef set points = self.actual_state_colors[color0]
        cdef int iy, ix, xx, yy
        
        for iy in [-1, 0, 1]:
            for ix in [-1, 0, 1]:
                if ix == 0 and iy == 0: continue
                xx, yy = self.periodic_normalize_x(x + ix), self.periodic_normalize_y(y + iy)
                if f"({xx},{yy})" in points:
                    alive_count += 1
        return alive_count

    cdef tuple get_color_counts_from_possible_neighbors(self, int x, int y, int color, list possible_dead_neighbors_list):
        cdef int color0 = color - 1
        cdef set points = self.actual_state_colors[color0]
        cdef int count = 0
        cdef int z = 0
        cdef int iy, ix, xx, yy
        
        for iy in [-1, 0, 1]:
            for ix in [-1, 0, 1]:
                if ix == 0 and iy == 0: continue
                xx, yy = self.periodic_normalize_x(x + ix), self.periodic_normalize_y(y + iy)
                if f"({xx},{yy})" in points:
                    possible_dead_neighbors_list[z] = None
                    count += 1
                z += 1
        return count, possible_dead_neighbors_list

    cdef bint is_alive(self, int x, int y):
        x, y = self.periodic_normalize_x(x), self.periodic_normalize_y(y)
        cdef str rep = f"({x},{y})"
        return rep in self.actual_state_colors[0] or rep in self.actual_state_colors[1] or rep in self.actual_state_colors[2]

    cdef bint is_dead_wait(self, int x, int y):
        cdef str rep = f"({x},{y})"
        cdef int c, color0
        for c in range(self.rule_c-2):
            for color0 in range(3):
                if rep in self.dead_wait_colors_n[c][color0]:
                    return True
        return False

    cdef int get_cell_color(self, int x, int y):
        cdef str rep = f"({x},{y})"
        cdef int i
        for i in range(3):
            if rep in self.actual_state_colors[i]:
                return i+1
        return 0

    cdef void add_alive_cell(self, int x, int y, int color):
        res = self.add_cell_to_custom_state(x, y, self.actual_state, self.actual_state_colors, color)
        self.actual_state = res[0]
        self.actual_state_colors = res[1]

    cdef tuple add_cell_to_custom_state(self, int x, int y, list state, list color_set, int color):
        cdef int color0 = color-1
        cdef int i
        cdef str rep
        
        if not (0 <= color0 < 3):
            raise Exception(f"Invalid color {color} for cell ({x},{y})")

        rep = f"({x},{y})"
        for i in range(3):
            if i != color0 and rep in color_set[i]:
                return state, color_set # Do not add duplicate cell with different color

        state = self._add_cell(x, y, state)
        color_set[color0].add(rep)
        return state, color_set

    cdef list _add_cell(self, int x, int y, list state):
        x = self.periodic_normalize_x(x)
        y = self.periodic_normalize_y(y)
        cdef int i, insertion_index
        cdef list row
        cdef bint added

        if not state:
            return [[y, x]]
        if y < state[0][0]:
            return [[y, x]] + state
        if y > state[-1][0]:
            return state + [[y, x]]
        
        return self._insert_into_state(x, y, state)

    cdef int _insertion_index(self, int x, list row):
        cdef int i, xval
        for i in range(len(row)-1):
            # row[1:] -> row[i+1]
            xval = row[i+1]
            if x < xval:
                return i+1
        return len(row)

    cdef list _insert_into_state(self, int x, int y, list state):
        cdef bint added = False
        cdef int i, insertion_index
        cdef list row
        
        for i in range(len(state)):
            row = state[i]
            if row[0] == y:
                if x in row[1:]: return state # Already exists
                insertion_index = self._insertion_index(x, row)
                state[i] = row[:insertion_index] + [x] + row[insertion_index:]
                added = True
                break
            elif y < row[0]:
                state.insert(i, [y, x])
                added = True
                break
        if not added:
             raise Exception(f"Failed to add cell ({x},{y})")
        return state

    cdef bint approx_equal(self, double a, double b, double tol):
        return self.relative_diff(a, b) < tol

    cdef double relative_diff(self, double a, double b):
        cdef double SMOL = 1e-12
        cdef double denom = max(abs(a), abs(b), SMOL)
        return abs(a - b) / denom

    cdef int _periodic_normalize(self, int q, int p):
        return q % p

    cdef int periodic_normalize_x(self, int x):
        return self._periodic_normalize(x, self.columns)

    cdef int periodic_normalize_y(self, int y):
        return self._periodic_normalize(y, self.rows)
