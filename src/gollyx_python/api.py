"""
Public API for gollyx-python.
"""

import json
from collections import deque
from .toroidal import ToroidalGOL as ToroidalGOLImpl
from .star import StarGOL as StarGOLImpl

class BaseGOL:
    """
    Base class for Game of Life implementations.
    """

    def __init__(self, **kwargs):
        self.generation = 0
        self.team_names = []
        self.live_counts_history = deque(maxlen=280) # a larger history for better victor checking
        self.running = True
        self.load_config(**kwargs)
        self.create_life()

    def load_config(self, **kwargs):
        """
        Load configuration from user-provided input params.
        """
        if "s1" in kwargs and "s2" in kwargs:
            self.ic1 = json.loads(kwargs["s1"])
            self.ic2 = json.loads(kwargs["s2"])
        else:
            raise Exception("ERROR: s1 and s2 parameters must both be specified")

        if "rows" in kwargs and "columns" in kwargs:
            self.rows = kwargs["rows"]
            self.columns = kwargs["columns"]
        else:
            raise Exception(
                "ERROR: rows and columns parameters must be provided to GOL constructor"
            )

        # The underlying simulation engine (star.py) expects birth and survival rules
        # as a string of digits (e.g., '23') for checking neighbor counts.
        # However, it's often more convenient for a developer to pass these as lists of
        # integers (e.g., [2, 3]). The following code handles this conversion.
        rule_b = kwargs.get('rule_b', '3')
        if isinstance(rule_b, list):
            rule_b = "".join(map(str, rule_b))

        rule_s = kwargs.get('rule_s', '23')
        if isinstance(rule_s, list):
            rule_s = "".join(map(str, rule_s))

        # The 'dead_wait' rule (rule_c) is also passed as a string for consistency,
        # even though it's converted to an integer for numerical comparisons in the engine.
        rule_c = kwargs.get('rule_c', '4')

        self.rules = {
            'birth': str(rule_b),
            'survival': str(rule_s),
            'dead_wait': str(rule_c)
        }

        self.halt = kwargs.get("halt", True)
        self.periodic = kwargs.get("periodic", False)

        if "team1" in kwargs and "team2" in kwargs:
            self.team_names = [kwargs["team1"], kwargs["team2"]]
        else:
            self.team_names = ["Team 1", "Team 2"]

    def next_step(self):
        """
        Advance the simulation by one generation.
        """
        if not self.running:
            return self.get_live_counts()

        victor = self.check_for_victor()
        if victor and self.halt:
            self.running = False
            return self.get_live_counts()

        self.life.next_generation()
        self.generation += 1
        live_cells_c1, live_cells_c2 = self.life.get_live_cells()
        self.live_counts_history.append((len(live_cells_c1), len(live_cells_c2)))
        return self.get_live_counts()

    def get_live_counts(self):
        """
        Get the number of live cells for each color.
        """
        raise NotImplementedError

    def check_for_victor(self):
        """
        Check for a victor based on a stable moving average of cell counts.
        """
        if len(self.live_counts_history) < 10:
            return None

        avg1 = sum(c[0] for c in self.live_counts_history) / len(self.live_counts_history)
        avg2 = sum(c[1] for c in self.live_counts_history) / len(self.live_counts_history)

        # Simplified victor check
        if self.live_counts_history[-1][0] > self.live_counts_history[-1][1] and all(c[0] > c[1] for c in list(self.live_counts_history)[-10:]):
             return self.team_names[0]
        if self.live_counts_history[-1][1] > self.live_counts_history[-1][0] and all(c[1] > c[0] for c in list(self.live_counts_history)[-10:]):
             return self.team_names[1]
        
        return None

    def create_life(self):
        raise NotImplementedError


class ToroidalGOL(BaseGOL):
    """
    Public API for the Toroidal Game of Life.
    """

    def create_life(self):
        self.life = ToroidalGOLImpl(self.columns, self.rows, self.rules)
        self.life.set_pattern(self.ic1, self.ic2)

    def get_live_counts(self):
        if not self.live_counts_history:
             live_cells_c1, live_cells_c2 = self.life.get_live_cells()
             counts = (len(live_cells_c1), len(live_cells_c2))
        else:
             counts = self.live_counts_history[-1]

        live_cells1 = counts[0]
        live_cells2 = counts[1]
        live_cells = live_cells1 + live_cells2
        
        total_area = self.rows * self.columns
        coverage = (live_cells / (total_area + 1e-12)) * 100
        
        victory_pct = 0
        if live_cells > 0:
            if live_cells1 > live_cells2:
                victory_pct = (live_cells1 / (live_cells)) * 100
            else:
                victory_pct = (live_cells2 / (live_cells)) * 100

        territory1 = (live_cells1 / (total_area + 1e-12)) * 100
        territory2 = (live_cells2 / (total_area + 1e-12)) * 100

        return {
            "generation": self.generation,
            "liveCells": live_cells,
            "liveCells1": live_cells1,
            "liveCells2": live_cells2,
            "victoryPct": victory_pct,
            "coverage": coverage,
            "territory1": territory1,
            "territory2": territory2,
        }


class StarGOL(BaseGOL):
    """
    Public API for the Star Game of Life (Generations).
    """

    def create_life(self):
        self.life = StarGOLImpl(self.columns, self.rows, self.rules, periodic=self.periodic)
        self.life.set_pattern(self.ic1, self.ic2)

    def next_step(self):
        if not self.running:
            return self.get_live_counts()

        victor = self.check_for_victor()
        if victor and self.halt:
            self.running = False
            return self.get_live_counts()

        self.life.next_generation()
        self.generation += 1
        live_cells_c1, live_cells_c2, live_cells_c3 = self.life.get_live_cells()
        self.live_counts_history.append((len(live_cells_c1), len(live_cells_c2), len(live_cells_c3)))
        return self.get_live_counts()

    def get_live_counts(self):
        if not self.live_counts_history:
             live_cells_c1, live_cells_c2, live_cells_c3 = self.life.get_live_cells()
             counts = (len(live_cells_c1), len(live_cells_c2), len(live_cells_c3))
        else:
             counts = self.live_counts_history[-1]

        live_cells_colors = [counts[0], counts[1], counts[2]]
        live_cells = sum(live_cells_colors)
        
        total_area = self.rows * self.columns
        coverage = (live_cells / (total_area + 1e-12)) * 100

        return {
            "generation": self.generation,
            "liveCells": live_cells,
            "liveCells1": live_cells_colors[0],
            "liveCells2": live_cells_colors[1],
            "liveCellsColors": live_cells_colors,
            "coverage": coverage,
        }
    
    def check_for_victor(self):
        # Simplified check for StarGOL, as it has 3 colors
        # The original logic is complex, this is a placeholder
        return None
