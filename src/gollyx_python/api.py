"""
Public API for gollyx-python.
"""

import json
from collections import deque
from .toroidal import ToroidalGOL
from .star import StarGOL

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
        ic1_val = kwargs.get("initialConditions1")
        ic2_val = kwargs.get("initialConditions2")

        if ic1_val is not None and ic2_val is not None:
            self.ic1 = json.loads(ic1_val)
            self.ic2 = json.loads(ic2_val)
        else:
            raise Exception("ERROR: initialConditions1 and initialConditions2 parameters must both be specified")

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

        # rule_c needs to be modified before storing in rules, so cast to int
        rule_c = int(kwargs.get('rule_c', '4'))

        self.rules = {
            # str
            'birth': str(rule_b),
            'survival': str(rule_s),
            # int
            'dead_wait': rule_c - 2,
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

    def load_config(self, **kwargs):
        """Load configuration specific to ToroidalGOL."""
        # ToroidalGOL defaults to periodic=True if not specified, 
        # whereas BaseGOL defaults to False.
        if "periodic" not in kwargs:
            kwargs["periodic"] = True
            
        super().load_config(**kwargs)
        self.maxdim = kwargs.get("maxdim", 280)

    def create_life(self):
        # Convert rules back to list of ints for ToroidalGOL
        # BaseGOL stores them as strings in self.rules, e.g., "23" -> [2, 3]
        rule_b_list = [int(d) for d in self.rules['birth']]
        rule_s_list = [int(d) for d in self.rules['survival']]

        self.life = ToroidalGOL(
            self.ic1,
            self.ic2,
            self.rows,
            self.columns,
            rule_b_list,
            rule_s_list,
            self.maxdim,
            self.halt,
        )
        # Ensure implementation syncs with config
        self.life.periodic = self.periodic

    def next_step(self):
        return self.life.next_step()

    def get_live_counts(self):
        return self.life.get_live_counts()

    def check_for_victor(self):
        return self.life.found_victor

    @property
    def running(self):
        return self.life.running
    
    @running.setter
    def running(self, value):
        if hasattr(self, 'life'):
            self.life.running = value
        # BaseGOL.__init__ sets self.running = True before create_life is called
        # We can safely ignore the assignment if self.life doesn't exist yet, 
        # as self.life will be initialized with running=True in its own __init__.
        pass

    @property
    def generation(self):
        return self.life.generation

    @generation.setter
    def generation(self, value):
        if hasattr(self, 'life'):
            self.life.generation = value
        pass


class StarGOL(BaseGOL):
    """
    Public API for the Star Game of Life (Generations).
    """

    def load_config(self, **kwargs):
        """
        Load configuration specific to StarGOL.
        """
        super().load_config(**kwargs)

        # Load dead-but-waiting initial conditions (optional)
        self.ic_b1 = json.loads(kwargs.get("initialConditionsb1", "[]"))
        self.ic_b2 = json.loads(kwargs.get("initialConditionsb2", "[]"))
        self.ic_c1 = json.loads(kwargs.get("initialConditionsc1", "[]"))
        self.ic_c2 = json.loads(kwargs.get("initialConditionsc2", "[]"))

    def create_life(self):
        self.life = StarGOL(self.columns, self.rows, self.rules, periodic=self.periodic)
        self.life.set_pattern(self.ic1, self.ic2, self.ic_b1, self.ic_b2, self.ic_c1, self.ic_c2)

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
        """
        Check for a victor based on the underlying simulation's state.
        """
        if self.life.found_victor:
            if self.life.who_won == 1:
                return self.team_names[0]
            elif self.life.who_won == 2:
                return self.team_names[1]
            else:
                # Tie or invalid win
                raise Exception("Game ended in a tie or invalid win state.")
        return None
