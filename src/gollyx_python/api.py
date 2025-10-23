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
        self.live_counts_history = deque(maxlen=10)
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

        self.rules = {
            'birth': kwargs.get('rule_b', '3'),
            'survival': kwargs.get('rule_s', '23'),
            'dead_wait': kwargs.get('rule_c', 8)
        }

        if "team1" in kwargs and "team2" in kwargs:
            self.team_names = [kwargs["team1"], kwargs["team2"]]
        else:
            self.team_names = ["Team 1", "Team 2"]

    def next_step(self):
        """
        Advance the simulation by one generation.
        """
        self.life.next_generation()
        self.generation += 1
        live_cells_c1, live_cells_c2 = self.life.get_live_cells()
        self.live_counts_history.append((len(live_cells_c1), len(live_cells_c2)))

    def get_live_counts(self):
        """
        Get the number of live cells for each color.
        """
        if not self.live_counts_history:
             live_cells_c1, live_cells_c2 = self.life.get_live_cells()
             return {"liveCells1": len(live_cells_c1), "liveCells2": len(live_cells_c2)}
        return {"liveCells1": self.live_counts_history[-1][0], "liveCells2": self.live_counts_history[-1][1]}

    def check_for_victor(self):
        """
        Check for a victor based on a stable moving average of cell counts.
        """
        if len(self.live_counts_history) < 10:
            return None

        avg1 = sum(c[0] for c in self.live_counts_history) / 10
        avg2 = sum(c[1] for c in self.live_counts_history) / 10

        if avg1 > avg2 and all(c[0] > c[1] for c in self.live_counts_history):
            return self.team_names[0]
        if avg2 > avg1 and all(c[1] > c[0] for c in self.live_counts_history):
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


class StarGOL(BaseGOL):
    """
    Public API for the Star Game of Life (Generations).
    """

    def create_life(self):
        self.life = StarGOLImpl(self.columns, self.rows, self.rules)
        self.life.set_pattern(self.ic1, self.ic2)
