"""
An implementation of the "Generations" rules, also known as Star GOL.
"""

class StarGOL:
    """
    An implementation of the "Generations" rules (Star GOL).
    """

    def __init__(self, width, height, rules):
        self.width = width
        self.height = height
        self.rules = rules
        self.grid = [[0] * width for _ in range(height)]

    def set_pattern(self, pattern_color1, pattern_color2):
        """
        Set the initial pattern of live cells.
        """
        for x, y in pattern_color1:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = 1
        for x, y in pattern_color2:
            if 0 <= x < self.width and 0 <= y < self.height:
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
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            cell_state = self.grid[ny][nx]
                            if cell_state == 1:
                                neighbors_color1 += 1
                            elif cell_state == 2:
                                neighbors_color2 += 1
                
                total_neighbors = neighbors_color1 + neighbors_color2
                cell_state = self.grid[y][x]

                if cell_state > 2: # Dead wait states
                    new_grid[y][x] = cell_state + 1 if cell_state < self.rules['dead_wait'] + 2 else 0
                elif cell_state in [1, 2]: # Live states
                    if str(total_neighbors) in self.rules['survival']:
                        if neighbors_color1 > neighbors_color2:
                            new_grid[y][x] = 1
                        elif neighbors_color2 > neighbors_color1:
                            new_grid[y][x] = 2
                        else:
                            new_grid[y][x] = cell_state
                    else:
                        new_grid[y][x] = 3 # Start dead wait
                else: # Dead state
                    if str(total_neighbors) in self.rules['birth']:
                        if neighbors_color1 > neighbors_color2:
                            new_grid[y][x] = 1
                        else:
                            new_grid[y][x] = 2
        
        self.grid = new_grid

    def get_live_cells(self):
        """
        Return the coordinates of all live cells.
        """
        live_cells_color1 = []
        live_cells_color2 = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    live_cells_color1.append((x, y))
                elif self.grid[y][x] == 2:
                    live_cells_color2.append((x, y))
        return live_cells_color1, live_cells_color2
