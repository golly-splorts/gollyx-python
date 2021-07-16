import json
from .pylife import DragonLife


class CA(object):
    team_names: list = []
    columns = 0
    rows = 0

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
                    color = self.life.get_cell_color(j, i)
                    if color == 1:
                        row += "#"
                    elif color == 2:
                        row += "o"
                    else:
                        row += "?"
                else:
                    row += "."
            row += "|"
            s.append(row)
        s.append("+" + "-" * (self.columns) + "+")
        rep = "\n".join(s)
        rep += "\n"

        livecounts = self.count()

        rep += "\nGeneration: %d" % (self.generation)
        rep += "\nLive cells, color 1: %d" % (livecounts["liveCells1"])
        rep += "\nLive cells, color 2: %d" % (livecounts["liveCells2"])
        rep += "\nLive cells, total: %d" % (livecounts["liveCells"])

        return rep

    def load_config(self, **kwargs):
        """
        Load configuration from user-provided input params
        """

        # Initial conditions
        if "s1" in kwargs and "s2" in kwargs:
            self.ic1 = kwargs["s1"]
            self.ic2 = kwargs["s2"]
        else:
            raise Exception("ERROR: s1 and s2 parameters must both be specified")

        # Rule string
        rulestr = ""
        if "rule" in kwargs:
            rulestr = str(kwargs["rule"])
            if len(rulestr) != 27:
                err = "ERROR: three-state rule strings must have length 27, "
                err += f"yours has length {len(rulestr)}"
                raise Exception(err)
            for c in rulestr:
                if c not in ["0", "1", "2"]:
                    raise Exception("ERROR: three-state rule strings must contain only {0,1,2}")
        else:
            raise Exception("ERROR: no 'rule' kwarg specified!")

        # Ternary rule string
        self.rule = rulestr

        # Grid size
        if "rows" in kwargs and "columns" in kwargs:
            self.rows = kwargs["rows"]
            self.columns = kwargs["columns"]
        else:
            raise Exception(
                "ERROR: rows and columns parameters must be provided to CA constructor"
            )

        # Team names
        if "team1" in kwargs and "team2" in kwargs:
            self.team_names = [kwargs["team1"], kwargs["team2"]]
        else:
            self.team_names = ["Team 1", "Team 2"]

        # Whether to stop when a victor is detected
        if "halt" in kwargs:
            self.halt = kwargs["halt"]
        else:
            self.halt = True

    def create_life(self):
        try:
            ic1 = json.loads(self.ic1)
        except json.decoder.JSONDecodeError:
            err = "ERROR: Could not load data as json:\n"
            err += self.ic1
            raise Exception(err)

        try:
            ic2 = json.loads(self.ic2)
        except json.decoder.JSONDecodeError:
            err = "ERROR: Could not load data as json:\n"
            err += self.ic1
            raise Exception(err)

        rule = self.rule

        self.life = DragonLife(
            ic1,
            ic2,
            rule,
            self.rows,
            self.columns,
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
