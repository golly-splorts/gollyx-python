import json
from .pylife import BinaryLife


class GOL(object):
    team_names: list = []
    columns = 0
    rows = 0
    rule_b: list = []
    rule_s: list = []

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
        rep += "\nVictory Percent: %0.1f %%" % (livecounts["victoryPct"])
        rep += "\nCoverage: %0.2f %%" % (livecounts["coverage"])
        rep += "\nTerritory, color 1: %0.2f %%" % (livecounts["territory1"])
        rep += "\nTerritory, color 2: %0.2f %%" % (livecounts["territory2"])

        return rep

    def load_config(self, **kwargs):
        """Load configuration from user-provided input params"""
        if "s1" in kwargs and "s2" in kwargs:
            self.ic1 = kwargs["s1"]
            self.ic2 = kwargs["s2"]
        else:
            raise Exception("ERROR: s1 and s2 parameters must both be specified")

        if "rows" in kwargs and "columns" in kwargs:
            self.rows = kwargs["rows"]
            self.columns = kwargs["columns"]
        else:
            raise Exception(
                "ERROR: rows and columns parameters must be provided to GOL constructor"
            )

        if "rule_b" in kwargs:
            self.rule_b = [int(j) for j in kwargs['rule_b']]
        else:
            self.rule_b = [3]
        if "rule_s" in kwargs:
            self.rule_s = [int(j) for j in kwargs['rule_s']]
        else:
            self.rule_s = [2, 3]

        if "team1" in kwargs and "team2" in kwargs:
            self.team_names = [kwargs["team1"], kwargs["team2"]]
        else:
            self.team_names = ["Team 1", "Team 2"]

        # Whether to stop when a victor is detected
        if "halt" in kwargs:
            self.halt = kwargs["halt"]
        else:
            self.halt = True

        # Neighbor color legacy mode was used in Seasons 1-3
        if "neighbor_color_legacy_mode" in kwargs:
            self.neighbor_color_legacy_mode = kwargs["neighbor_color_legacy_mode"]
        else:
            self.neighbor_color_legacy_mode = False

    def create_life(self):
        try:
            ic1 = json.loads(self.ic1)
        except json.decoder.JSONDecodeError:
            err = "Error: Could not load data as json:\n"
            err += self.ic1
            raise Exception(err)

        try:
            ic2 = json.loads(self.ic2)
        except json.decoder.JSONDecodeError:
            err = "Error: Could not load data as json:\n"
            err += self.ic1
            raise Exception(err)

        self.life = BinaryLife(
            ic1,
            ic2,
            self.rows,
            self.columns,
            self.rule_b,
            self.rule_s,
            self.halt,
            self.neighbor_color_legacy_mode,
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
