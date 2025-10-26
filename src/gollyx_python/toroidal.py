class ToroidalGOL:
    """
    An implementation of a toroidal Game of Life.
    """

    def __init__(self, width, height, rules):
        self.width = width
        self.height = height
        self.rules = rules
        self.live_cells_color1 = set()
        self.live_cells_color2 = set()

    def set_pattern(self, pattern_color1, pattern_color2):
        """
        Set the initial pattern of live cells.
        """
        for d in pattern_color1:
            y_str, xs = list(d.items())[0]
            y = int(y_str)
            for x in xs:
                self.live_cells_color1.add((x, y))

        for d in pattern_color2:
            y_str, xs = list(d.items())[0]
            y = int(y_str)
            for x in xs:
                self.live_cells_color2.add((x, y))

    def next_generation(self):
        """
        Compute the next generation of the Game of Life.
        """
        next_live_cells_color1 = set()
        next_live_cells_color2 = set()

        candidates = set()
        for x, y in self.live_cells_color1:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    candidates.add(((x + dx) % self.width, (y + dy) % self.height))
        for x, y in self.live_cells_color2:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    candidates.add(((x + dx) % self.width, (y + dy) % self.height))

        for x, y in candidates:
            neighbors_color1 = 0
            neighbors_color2 = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = ((x + dx) % self.width, (y + dy) % self.height)
                    if neighbor in self.live_cells_color1:
                        neighbors_color1 += 1
                    if neighbor in self.live_cells_color2:
                        neighbors_color2 += 1
            
            total_neighbors = neighbors_color1 + neighbors_color2
            is_live_color1 = (x, y) in self.live_cells_color1
            is_live_color2 = (x, y) in self.live_cells_color2
            is_live = is_live_color1 or is_live_color2

            if is_live:
                if str(total_neighbors) in self.rules['survival']:
                    if neighbors_color1 > neighbors_color2:
                        next_live_cells_color1.add((x, y))
                    elif neighbors_color2 > neighbors_color1:
                        next_live_cells_color2.add((x, y))
                    elif is_live_color1:
                        next_live_cells_color1.add((x, y))
                    else:
                        next_live_cells_color2.add((x, y))

            else: # birth
                if str(total_neighbors) in self.rules['birth']:
                    if neighbors_color1 > neighbors_color2:
                        next_live_cells_color1.add((x, y))
                    else:
                        next_live_cells_color2.add((x, y))

        self.live_cells_color1 = next_live_cells_color1
        self.live_cells_color2 = next_live_cells_color2

    def get_live_cells(self):
        """
        Return the coordinates of all live cells.
        """
        return self.live_cells_color1, self.live_cells_color2
