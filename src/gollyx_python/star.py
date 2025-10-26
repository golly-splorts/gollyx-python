class StarGOL:
    """
    An implementation of the star wars cellular automata.
    """

    def __init__(self, width, height, rules, periodic=True):
        self.width = width
        self.height = height
        self.rules = rules
        self.grid = [[0] * width for _ in range(height)]
        self.periodic = periodic

    def set_pattern(self, pattern_color1, pattern_color2):
        """
        Set the initial pattern of live cells.
        """
        for d in pattern_color1:
            y_str, xs = list(d.items())[0]
            y = int(y_str)
            for x in xs:
                if 0 <= y < self.height and 0 <= x < self.width:
                    self.grid[y][x] = 1
        for d in pattern_color2:
            y_str, xs = list(d.items())[0]
            y = int(y_str)
            for x in xs:
                if 0 <= y < self.height and 0 <= x < self.width:
                    self.grid[y][x] = 2

    def next_generation(self):
        """
        Compute the next generation of the Game of Life.
        """
        new_grid = [[0] * self.width for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                neighbors_color1 = 0
                neighbors_color2 = 0
                neighbors_color3 = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        nx, ny = x + dx, y + dy
                        if self.periodic:
                            nx = nx % self.width
                            ny = ny % self.height
                        
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            cell_state_neighbor = self.grid[ny][nx]
                            if cell_state_neighbor == 1:
                                neighbors_color1 += 1
                            elif cell_state_neighbor == 2:
                                neighbors_color2 += 1
                            elif cell_state_neighbor == 3:
                                neighbors_color3 += 1
                
                total_neighbors = neighbors_color1 + neighbors_color2 + neighbors_color3
                cell_state = self.grid[y][x]

                if cell_state >= 4: # Dead wait states
                    if cell_state < 3 + int(self.rules['dead_wait']):
                        new_grid[y][x] = cell_state + 1
                    else:
                        new_grid[y][x] = 0
                elif cell_state in [1, 2, 3]: # Live states
                    if str(total_neighbors) in self.rules['survival']:
                        if neighbors_color1 > neighbors_color2:
                            new_grid[y][x] = 1
                        elif neighbors_color2 > neighbors_color1:
                            new_grid[y][x] = 2
                        else:
                            new_grid[y][x] = cell_state
                    else:
                        new_grid[y][x] = 4 # Start dead wait
                else: # Dead state
                    if str(total_neighbors) in self.rules['birth']:
                        if neighbors_color1 > neighbors_color2:
                            new_grid[y][x] = 1
                        elif neighbors_color2 > neighbors_color1:
                            new_grid[y][x] = 2
                        else:
                            new_grid[y][x] = 3
        
        self.grid = new_grid

    def get_live_cells(self):
        """
        Return the coordinates of all live cells.
        """
        live_cells_color1 = []
        live_cells_color2 = []
        live_cells_color3 = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    live_cells_color1.append((x, y))
                elif self.grid[y][x] == 2:
                    live_cells_color2.append((x, y))
                elif self.grid[y][x] == 3:
                    live_cells_color3.append((x, y))
        return live_cells_color1, live_cells_color2, live_cells_color3
