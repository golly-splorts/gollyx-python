import math
from operator import indexOf


class StarBinaryGenerationsCA(object):

    running_avg_window: list = []
    running_avg_last3: list = []

    generation = 0
    columns = 0
    rows = 0

    row_b: list = []
    row_s: list = []
    row_c: list = []

    livecells = 0
    livecellscolors = []

    victory = 0.0
    who_won = 0
    coverage = 0.0

    found_victor = False
    running_avg_window: list = []
    running_avg_last3: list = [0.0, 0.0, 0.0]
    running = False
    periodic = True

    found_victor: bool = False

    # These are star cup defaults
    # Many bothans died to find these tolerances
    tol_zero = 1e-8
    tol_stable = 1e-6

    MAXDIM = 280

    def __init__(
        self,
        ic1: dict,
        ic2: dict,
        rows: int,
        columns: int,
        rule_b: list = [],
        rule_s: list = [],
        rule_c: int = -1,
        halt: bool = True,
        periodic: bool = True,
        tol_zero: float = None,
        tol_stable: float = None,
    ):
        self.ic1 = ic1
        self.ic2 = ic2

        self.rows = rows
        self.columns = columns

        self.rule_b = rule_b
        self.rule_s = rule_s
        self.rule_c = rule_c

        # Tolerances
        if tol_zero is not None:
            self.tol_zero = tol_zero
        if tol_stable is not None:
            self.tol_stable = tol_stable
        if self.tol_zero < 0 or self.tol_stable < 0:
            raise Exception(f"Error: tolerances must be > 0")

        # Initialize alive states
        self.actual_state = []
        self.actual_state_colors = [None, None, None]
        for j in range(3):
            self.actual_state_colors[j] = set()

        # Initialize dead wait states
        # This is an array of states,
        # and each state is an array of arrays.
        # The number of dead wait states is c-2.
        # The 2 accounts for alive/dead.
        self.dead_wait_n = []
        self.dead_wait_colors_n = []
        for i in range(self.rule_c - 2):
            dead_wait_j = []
            self.dead_wait_n.append(dead_wait_j)

            dead_wait_color_j = [None, None, None]
            for j in range(3):
                dead_wait_color_j[j] = set()
            self.dead_wait_colors_n.append(dead_wait_color_j)

        # Whether to stop when a victor is detected
        self.halt = halt

        self.running = True
        self.generation = 0

        self.running_avg_window = [
            0,
        ] * self.MAXDIM
        self.running_avg_last3 = [0, 0, 0]
        self.found_victor = False

        self.periodic = periodic

        self.set_initial_state()

        # This is the end of the constructor,
        # and the end of the parent constructor,
        # and the last thing called when initializing the manager.
        # Next thing that happens is calling next step.

    def set_initial_state(self):
        """similar to setInitialState in js simulator"""
        s1 = self.ic1
        s2 = self.ic2

        color = 1
        for s1row in s1:
            for y in s1row:
                yy = int(y)
                for xx in s1row[y]:
                    self.add_alive_cell(xx, yy, color)

        color = 2
        for s2row in s2:
            for y in s2row:
                yy = int(y)
                for xx in s2row[y]:
                    self.add_alive_cell(xx, yy, color)

        livecounts = self.get_live_counts()
        self.update_moving_avg(livecounts)

    def check_for_victor(self):
        if self.found_victor:
            return True
        else:
            return False

    def update_moving_avg(self, livecounts = None):
        """similar to checkForVictor in js simulator"""
        if livecounts is None:
            livecounts = self.get_live_counts()

        if not self.found_victor:
            maxdim = self.MAXDIM
            # maxdim = max(2 * self.columns, 2 * self.rows)

            rootsum = 0
            # This should be 2, not 3 (refs don't count)
            for i in range(2):
                rootsum += livecounts['liveCellsColors'][i]**2
            rootsum = math.sqrt(rootsum)

            #print(f"{self.generation} - {rootsum} - {livecounts['liveCellsColors']}")

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

    def next_step(self):
        """
        basically a wrapper for next_generation method
        """
        if self.running is False:
            return self.get_live_counts()
        elif self.halt and self.found_victor:
            self.running = False
            return self.get_live_counts()
        else:
            self.generation += 1
            live_counts = self.next_generation()
            self.update_moving_avg(live_counts)
            return live_counts

    def next_generation(self):
        """
        Evolve the actual_state list life state to the next generation.
        """
        all_dead_neighbors = {}

        # -----
        # init
        new_state = []
        new_state_colors = []
        for i in range(3):
            new_state_colors.append(set())

        new_dead_wait_n = []
        new_dead_wait_colors_n = []
        for i in range(self.rule_c - 2):
            new_dead_wait_j = []
            new_dead_wait_n.append(new_dead_wait_j)

            new_dead_wait_colors_j = []
            for i in range(3):
                new_dead_wait_colors_j.append(set())
            new_dead_wait_colors_n.append(new_dead_wait_colors_j)
        # -----

        # -----
        # SURVIVE step

        for i in range(len(self.actual_state)):

            # self.top_pointer = 1
            # self.bottom_pointer = 1

            for j in range(1, len(self.actual_state[i])):
                x = self.actual_state[i][j]
                y = self.actual_state[i][0]

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

                # create a list of possible dead neighbors
                # get_neighbors_from_alive() will pare this down
                dead_neighbors = [
                    [xm1, ym1, 1],
                    [x, ym1, 1],
                    [xp1, ym1, 1],
                    [xm1, y, 1],
                    [xp1, y, 1],
                    [xm1, yp1, 1],
                    [x, yp1, 1],
                    [xp1, yp1, 1],
                ]

                #if x==41 and y==11:
                #    import pdb; pdb.set_trace()
                #    a=0
                result, dead_neighbors = self.get_neighbors_from_alive(x, y, dead_neighbors)

                neighbors = result["neighbors"]
                color = result["color"]

                # join dead neighbors remaining to check list
                for dead_neighbor in dead_neighbors:
                    if dead_neighbor is not None:
                        # this cell is dead
                        xx = dead_neighbor[0]
                        yy = dead_neighbor[1]
                        key = str(xx) + "," + str(yy)

                        if not self.is_dead_wait(xx, yy):
                            # counting number of dead neighbors
                            if key not in all_dead_neighbors:
                                all_dead_neighbors[key] = 1
                            else:
                                all_dead_neighbors[key] += 1

                # Survive counts
                cell_survives = neighbors in self.rule_s
                if cell_survives:
                    # Keep cell alive
                    new_state, new_state_colors = self.add_cell_to_custom_state(
                        x, y, new_state, new_state_colors, color
                    )
                else:
                    # Kill cell, enter dead wait
                    new_dead_wait_n[0], new_dead_wait_colors_n[0] = self.add_cell_to_custom_state(
                        x, y, new_dead_wait_n[0], new_dead_wait_colors_n[0], color
                    )

        # End survive step
        # -----

        # -----
        # BIRTH step

        # Iterate over dead neighbors, determine if any will be born
        # (all dead neighbors only contains cells not in dead wait)
        for key in all_dead_neighbors:
            cell_born = (all_dead_neighbors[key] in self.rule_b)
            if cell_born:
                # This cell is dead, but has enough neighbors
                # that are alive that it will make new life
                key = key.split(",")
                t1 = int(key[0])
                t2 = int(key[1])

                # Get color from neighboring parent cells
                color = self.get_color_from_alive(t1, t2)

                new_state, new_state_colors = self.add_cell_to_custom_state(t1, t2, new_state, new_state_colors, color)

        # End birth step
        # -----

        # -----
        # DEAD WAIT CYCLING step

        # The 2 accounts for alive/dead states, -1 accounts for 0-based index
        cmax_ix = (self.rule_c - 1) - 2
        for c in range(cmax_ix, 0, -1):
            cm1 = c - 1

            # Shift dead wait N-1 back to N
            # Note: doing a deepcopy here takes a lot of time
            new_dead_wait_n[c] = self.dead_wait_n[cm1]

            # Shift new dead wait color sets to old dead wait color sets of prior step
            # First, construct list of different empty sets
            color_sets = [None, None, None]
            for i in range(3):
                s = set(list(self.dead_wait_colors_n[cm1][i]))
                color_sets[i] = s
            new_dead_wait_colors_n[c] = color_sets

        # end cycling step
        # -----

        self.actual_state = new_state
        self.actual_state_colors = new_state_colors

        self.dead_wait_n = new_dead_wait_n
        self.dead_wait_colors_n = new_dead_wait_colors_n

        return self.get_live_counts()

    # --------------------
    # helper methods for counting

    def _get_state_count(self, state):
        live = 0
        for i, state_row in enumerate(state):
            for j in range(1, len(state_row)):
                x = state_row[j]
                y = state_row[0]
                # shouldn't need these checks, but just to be sure
                if (y>=0 and y < self.rows and x >= 0 and x < self.columns):
                    live += 1
        return live

    def get_live_counts(self):
        """
        Get live counts of cells of each color, and total.
        Compute statistics.
        """
        livecells = self._get_state_count(self.actual_state)
        livecells_colors = [0,]*3
        livecells_sum = 0
        for i in range(3):
            ncells = len(self.actual_state_colors[i])
            livecells_colors[i] = ncells
            livecells_sum += ncells
        
        if livecells_sum != livecells:
            err = f"Error: get_live_counts returned inconsistent alive and color counts: "
            err += f"alive = {livecells}, sum of colors = {livecells_sum}"
            raise Exception(err)

        total_area = self.columns * self.rows
        coverage = (livecells / (1.0 * total_area))*100
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

    # ----------
    # helper methods for determining birth and survive colors

    def get_neighbors_from_alive(self, x, y, possible_neighbors_list):
        """
        Determine the number of neighbor cells of an alive cell (x,y) that are also alive.
        Returns a json struct with the color and number of neighbors, and the 
        possible (dead) neighbors list with alive neighbors set to None.

        Currently we also use dead wait colors as a tiebreaker for majority rules color.
        If things are still tied after including dead wait colors, keep the cell's
        current color. This method is only called on alive cells.

        Algorithm:
        - iterate over each possible dead neighbor coordinate
        - set the coordinate to undefined if neighbor is alive
        - accumulate alive neighbors counter for each color
        - use color counters to determine final color
        """
        # x and y are already normalized for periodic grid
        state = self.actual_state

        # Assemble color counts 
        neighbors = 0
        neighbors_norefs = 0
        neighbors_colors = [0,]*3
        for i in range(3):
            # Include state 3 (referees)
            count, possible_neighbors_list = self.get_color_counts_from_possible_neighbors(x, y, i+1, possible_neighbors_list)
            neighbors_colors[i] = count
        neighbors = sum(neighbors_colors)
        neighbors_norefs = neighbors_colors[0] + neighbors_colors[1]

        # Assemble dead wait counts
        neighbors_dw = [0,]*3
        # Loop over colors
        for i in range(3-1):
            # Exclude state 3 (referees) from color determinations
            count = self.get_color_counts_from_dead_wait(x, y, i+1)
            neighbors_dw[i] = count

        # Determine number of neighbors, and majority color.
        # This procedure is only applied to surviving cells.

        # Final color returned
        # 0 means no alive colors/cells
        # 1 2 3 mean colors 1 2 3
        # -1 means tie
        color = 0
        
        # Check if any neighbors are alive
        if neighbors > 0:

            # Check if any non-referee neighbors are alive
            if neighbors_norefs > 0:

                # Only goal is to determine if there is a tie
                # in the number of neighbors of color 1 and 2,
                # which requires counting how many colors have
                # a value equal to max(neighbors color 1, neighbors color 2)
                max_neighbor = max(neighbors_colors[0], neighbors_colors[1])
                num_equal_max = 0
                if neighbors_colors[0]==max_neighbor:
                    num_equal_max += 1
                    color = 1
                if neighbors_colors[1]==max_neighbor:
                    num_equal_max += 1
                    color = 2

                # 2 = number of non-referee teams
                if num_equal_max == 2:

                    # Two colors both have max value, meaning tie.
                    # Repeat same procedure as above, but this time including dead wait.
                    max_neighbor_dw = max(neighbors_colors[0]+neighbors_dw[0], neighbors_colors[1]+neighbors_dw[1])
                    num_equal_max_dw = 0
                    # (was using wrong variable in these if checks, big hassle to track down that bug)
                    if neighbors_colors[0]+neighbors_dw[0]==max_neighbor_dw:
                        num_equal_max_dw += 1
                        color = 1
                    if neighbors_colors[1]+neighbors_dw[1]==max_neighbor_dw:
                        num_equal_max_dw += 1
                        color = 2

                    if num_equal_max_dw == 2:
                        # Still have a tie, even with dead wait taken into account
                        color = -1
            else:
                color = -1
            # end if non-ref neighbors
        else:
            color = -1
        # end if alive neighbors

        if color < 0:
            color = self.get_cell_color(x, y)

        return dict(neighbors=neighbors, color=color), possible_neighbors_list

    def get_color_from_alive(self, x, y):
        """
        This function seems redundant, but is slightly different.
        The above function is for dead cells that become alive.
        This function is for dead cells that come alive because of THOSE cells.
        """
        # x and y are already normalized

        # Determine color of new birthed cell by determining number of neighbors
        # of each color, majority color wins.

        # This (x,y) cell is currently dead, so this check is slightly different
        # from get_neighbors_from_alive, which is for alive cells.

        neighbors = 0
        neighbors_norefs = 0
        neighbors_colors = [0,]*3
        for i in range(3):
            count = self.get_color_counts_from_alive(x, y, i+1)
            neighbors_colors[i] = count
        neighbors = sum(neighbors_colors)
        neighbors_norefs = neighbors_colors[0] + neighbors_colors[1]

        # This is the return value: color of birthed cell
        color = 0

        # Check if any neighbors are alive
        if neighbors > 0:

            # Check if any non-referee neighbors are alive
            if neighbors_norefs > 0:

                max_neighbor = max(neighbors_colors[0], neighbors_colors[1])
                num_equal_max = 0
                if neighbors_colors[0]==max_neighbor:
                    num_equal_max += 1
                    color = 1
                if neighbors_colors[1]==max_neighbor:
                    num_equal_max += 1
                    color = 2

                # 2 = number of non-referee teams
                if num_equal_max == 2:
                    # Two colors both have max value, meaning tie.
                    # In the case of ties, throw the new cell to the referees
                    # (don't bother checking dead wait)
                    color = 3

            else:
                # No live non-referee neighbors, so throw to the refs
                color = 3
            # end if non-ref neighbors
        else:
            # No live neighbors
            # (should not be here)
            color = 0

        return color

    # ----------
    # utility methods

    # It seems that the method of storing all points in a set of strings is too slow.
    # The old method of iterating over every point is faster (how is that even possible)
    # Could use a _get_color_counts_from_state method, walk through all points,
    # keep track of which points in the stencil are which [i][j] coordinate
    # (periodic means you have to check em all)

    def get_color_counts_from_dead_wait(self, x, y, color):
        """
        Count the number of dead wait neighbors of cell (x,y) that have the specified color.
        This is used in tiebreakers when determining color of alive cells via majority rule.
        """
        # x and y are already normalized

        color0 = color - 1
        dead_wait_count = 0
        for c in range(self.rule_c-2):
            points = self.dead_wait_colors_n[c][color0]
            for iy in [-1, 0, 1]:
                for ix in [-1, 0, 1]:
                    if not (ix==0 and iy==0):
                        xx = x + ix
                        yy = y + iy
                        if self.periodic:
                            xx = self.periodic_normalize_x(xx)
                            yy = self.periodic_normalize_y(yy)
                        rep = f"({xx},{yy})"
                        if rep in points:
                            dead_wait_count += 1
        return dead_wait_count

    def get_color_counts_from_alive(self, x, y, color):
        """
        Count the number of alive neighbors of cell (x,y) that have the specified color.
        """
        # x and y are already normalized

        color0 = color - 1
        alive_count = 0
        for iy in [-1, 0, 1]:
            for ix in [-1, 0, 1]:
                if not (ix==0 and iy==0):
                    xx = x + ix
                    yy = y + iy
                    if self.periodic:
                        xx = self.periodic_normalize_x(xx)
                        yy = self.periodic_normalize_y(yy)
                    rep = f"({xx},{yy})"
                    if rep in self.actual_state_colors[color0]:
                        alive_count += 1
        return alive_count

    def get_color_counts_from_possible_neighbors(self, x, y, color, possible_dead_neighbors_list):
        """
        Count the number of alive neighbors of cell (x,y) that have the specified color,
        and eliminate them from the possible dead neighbors list
        """
        # x and y are already normalized
        color0 = color - 1
        points = self.actual_state_colors[color0]
        count = 0
        z = 0
        for iy in [-1, 0, 1]:
            for ix in [-1, 0, 1]:
                if not (ix==0 and iy==0):
                    xx = x + ix
                    yy = y + iy
                    if self.periodic:
                        xx = self.periodic_normalize_x(xx)
                        yy = self.periodic_normalize_y(yy)
                    rep = f"({xx},{yy})"
                    if rep in points:
                        possible_dead_neighbors_list[z] = None
                        count += 1
                    z += 1
        return count, possible_dead_neighbors_list

    def is_alive(self, x, y):
        """
        Boolean function: is the cell at x, y alive
        """
        if self.periodic:
            x = self.periodic_normalize_x(x)
            y = self.periodic_normalize_y(y)

        rep = f"({x},{y})"
        for color0 in range(3):
            points = self.actual_state_colors[color0]
            if rep in points:
                return True

        return False

    '''
    def is_alive_old(self, x, y):
        """
        Boolean function: is the cell at x, y alive
        """
        if self.periodic:
            x = self.periodic_normalize_x(x)
            y = self.periodic_normalize_y(y)

        for row in self.actual_state:
            if row[0] == y:
                for c in row[1:]:
                    if c == x:
                        return True

        return False
    '''

    def is_dead_wait(self, x, y):
        """
        Boolean function: is the cell at x, y in a dead wait state
        """
        # x and y are already normalized
        rep = f"({x},{y})"
        for c in range(self.rule_c-2):
            for color0 in range(3):
                if rep in self.dead_wait_colors_n[c][color0]:
                    return True

        return False

    def get_cell_color(self, x, y):
        # x and y are already normalized
        rep = f"({x},{y})"
        for i in range(3):
            if rep in self.actual_state_colors[i]:
                return i+1
        return 0


    '''
    def get_dead_wait_color(self, x, y, c=-1):
        # x and y are already normalized
        rep = f"({x},{y})"
        if c < 0:
            # Do all c values
            cmin = 0
            cmax = self.rule_c - 2
        else:
            # Only do the c value specified
            cmin = c
            cmax = c+1

        for ic in range(cmin, cmax):
            for i in range(3):
                if rep in self.dead_wait_colors_n[ic][i]:
                    return i+1

        return 0
    '''

    def remove_not_alive_cell(self, x, y, color):
        self.actual_state, self.actual_state_colors = self.remove_cell_from_custom_state(x, y, self.actual_state, self.actual_state_colors, color)

    def remove_cell_from_custom_state(self, x, y, state, color_set, color):
        """
        removes the cell at (x,y) from the gien state and color set,
        and returns the state and color set.
        """
        color0 = color - 1
        if color0 >= 0 and color0 < 3:
            state = self._remove_cell(x, y, state)
            rep = f"({x},{y})"
            color_set[color0].discard(rep)
        else:
            err = f"Error: remove_cell_from_custom_state() called with invalid color {color}"
            raise Exception(err)
        return state, color_set

    def add_alive_cell(self, x, y, color):
        self.actual_state, self.actual_state_colors = self.add_cell_to_custom_state(x, y, self.actual_state, self.actual_state_colors, color)

    def add_cell_to_custom_state(self, x, y, state, color_set, color):
        """
        adds a new cell at (x,y) to the given state and color set,
        and returns the state and color set.
        """
        color0 = color-1
        if color0 >= 0 and color0 < 3:
            rep = f"({x},{y})"

            # Verify this cell is not alredy in another color set
            for i in range(3):
                if i!=color0:
                    if rep in color_set[i]:
                        #err = f"Error: add_cell_to_custom_state() asked to add duplicate cell from color {i+1} to color {color}"
                        #raise Exception(err)
                        return state, color_set

            # Add to alive state
            state = self._add_cell(x, y, state)

            # Add this point to set of points for specified color
            color_set[color0].add(rep)

        else:
            err = f"Error: add_cell_to_custom_state() called with invalid color {color} at cell ({x},{y})"
            raise Exception(err)
        
        return state, color_set

    def _add_cell(self, x, y, state):
        """
        Add point (x,y) to state, and return the new state
        """
        x = self.periodic_normalize_x(x)
        y = self.periodic_normalize_y(y)

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
            return self._insert_into_state(x, y, state)


    def _insertion_index(self, x, row):
        """Get the insertion index for the given x coordinate and listlife row"""
        for i, xval in enumerate(row[1:]):
            if x < xval:
                return i+1
        return len(row)


    def _insert_into_state(self, x, y, state):
        """Add point (x,y) into the middle of the listlife state"""
        added = False
        statelen = len(state)
        for i in range(statelen):
            row = state[i]
            if (not added) and (row[0] == y):
                # Check if point already here
                if x in row[1:]:
                    # Skip
                    return state
                # Figure out insertion index
                insertion_index = self._insertion_index(x, row)
                newrow = row[0:insertion_index] + [x] + row[insertion_index:]
                state[i] = newrow
                added = True
                break
            elif (not added) and (y < row[0]):
                # state does not include this row, so create new row
                new_row = [[y, x]]
                state = state[:i] + new_row + state[i:]
                added = True
                break
            else:
                pass

        if added is False:
            raise Exception(f"Error adding cell ({x},{y}) to state {state}")

        return state


    def _remove_cell(self, x, y, state):
        x = self.periodic_normalize_x(x)
        y = self.periodic_normalize_y(y)

        for i, row in enumerate(state):
            if row[0]==y:
                if len(row)==2:
                    # Remove entire row
                    state = state[:i] + state[i+1:]
                else:
                    j = indexOf(row, x)
                    state[i] = row[:j] + row[j+1:]
                break

        return state

    def approx_equal(self, a, b, tol):
        return self.relative_diff(a, b) < tol

    def relative_diff(self, a, b):
        SMOL = 1e-12
        denom = max(a + SMOL, b + SMOL)
        return abs(a - b) / (1.0 * denom)

    def _periodic_normalize(self, q, p):
        if q >= p or q < 0:
            return (q + p) % (p)
        else:
            return q

    def periodic_normalize_x(self, x):
        return self._periodic_normalize(x, self.columns)

    def periodic_normalize_y(self, y):
        return self._periodic_normalize(y, self.rows)


### def main():
###     gol = BinaryLife(
###         s1='[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
###         s2='[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
###         rows=120,
###         columns=100,
###     )
### 
###     while gol.running:
###         gol.next_step()
###         if gol.generation % 500 == 0:
###             print(f"Simulating generation {gol.generation}")
### 
###     from pprint import pprint
### 
###     pprint(gol.get_live_counts())


if __name__ == "__main__":
    main()
