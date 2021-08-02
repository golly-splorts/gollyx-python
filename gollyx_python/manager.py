import json
from .pylife import BinaryLife
from .pylife4 import QuaternaryLife


class GOL(object):
    team_names: list = []
    columns = 0
    rows = 0
    rule_b: list = []
    rule_s: list = []

    nteams: int

    def __init__(self, **kwargs):
        self.load_config(**kwargs)
        self.create_life()

    def __repr__(self):
        s = []
        s.append("+" + "-" * (self.columns) + "+")
        for i in range(self.rows):
            row = "|"
            for j in range(self.columns):
                if self.life.is_alive(j, i):
                    labels = "ABCDEFGHIJKLM"
                    color = self.life.get_cell_color(j, i)
                    row += labels[color-1]
                else:
                    row += "."
            row += "|"
            s.append(row)
        s.append("+" + "-" * (self.columns) + "+")
        rep = "\n".join(s)
        rep += "\n"

        livecounts = self.count()

        rep += "\nGeneration: %d" % (self.generation)
        for i in range(self.nteams):
            k = f"liveCells{i+1}"
            rep += f"\nLive cells, color {i+1}: %d" % (livecounts[k])
        rep += "\nLive cells, total: %d" % (livecounts["liveCells"])
        rep += "\nCoverage: %0.2f %%" % (livecounts["coverage"])

        return rep

    def load_config(self, **kwargs):
        """Load configuration from user-provided input params"""
        if "nteams" in kwargs:
            self.nteams = kwargs["nteams"]
        else:
            self.nteams = 2

        # s1 => self.ic1
        for i in range(self.nteams):
            k = f"s{i+1}"
            attr = f"ic{i+1}"
            if k in kwargs:
                setattr(self, attr, kwargs[k])

        # Check user provided all s{N} inputs
        for i in range(self.nteams):
            attr = f"ic{i+1}"
            val = getattr(self, attr, None)
            if val is None:
                k = f"s{i+1}"
                raise Exception("Error: input parameter {k} must be specified")

        if "rows" in kwargs and "columns" in kwargs:
            self.rows = kwargs["rows"]
            self.columns = kwargs["columns"]
        else:
            raise Exception(
                "Error: rows and columns parameters must be provided to GOL constructor"
            )

        if "rule_b" in kwargs:
            self.rule_b = [int(j) for j in kwargs['rule_b']]
        else:
            self.rule_b = [3]
        if "rule_s" in kwargs:
            self.rule_s = [int(j) for j in kwargs['rule_s']]
        else:
            self.rule_s = [2, 3]

        self.team_names = []
        for i in range(self.nteams):
            team_label = f"team{i+1}"
            if team_label in kwargs:
                self.team_names.append(kwargs[team_label])
            else:
                team_name = f"Team {i+1}"
                self.team_names.append(team_name)

        # Whether to stop when a victor is detected
        if "halt" in kwargs:
            self.halt = kwargs["halt"]
        else:
            self.halt = True

    def create_life(self):
        ics = []
        for i in range(self.nteams):
            attr = f"ic{i+1}"
            ic_str = getattr(self, attr, None)
            try:
                ic = json.loads(ic_str)
            except json.decoder.JSONDecodeError:
                err = "Error: Could not load initial conditions "
                err += f"for state {i+1}: JSON decoder error:\n"
                err += ic
                raise Exception(err)
            ics.append(ic)

        if self.nteams==2:
            self.life = BinaryLife(
                *ics,
                self.rows,
                self.columns,
                self.rule_b,
                self.rule_s,
                self.halt,
            )
        elif self.nteams==4:
            self.life = QuaternaryLife(
                *ics,
                self.rows,
                self.columns,
                self.rule_b,
                self.rule_s,
                self.halt,
            )

    def next_step(self):
        return self.life.next_step()

    def count(self):
        return self.life.get_live_counts()

    def check_for_victor(self):
        return self.life.check_for_victor()

    @property
    def running(self):
        return self.life.running

    @property
    def generation(self):
        return self.life.generation
