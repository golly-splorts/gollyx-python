import gollyx_python
import unittest
from .fixtures_star import (
    rainbowmath_120_180_finegrained_gold,
    rainbowmath_120_180_state1,
    rainbowmath_120_180_state2,
    rainbowmath_120_180_rows,
    rainbowmath_120_180_cols,
    rainbowmath_120_180_finegrained_gold,
    random_100_120_state1,
    random_100_120_state2,
    random_100_120_rows,
    random_100_120_cols,
    random_100_120_final,
)


class StarGenerationsTest(unittest.TestCase):

    star_wars_b = [2]
    star_wars_s = [3, 4, 5]
    star_wars_c = 4

    def test_constructor(self):
        """
        Test that we can successfully construct a Generations CA
        """
        gollyx_python.StarGOLGenerations(
            s1 = rainbowmath_120_180_state1,
            s2 = rainbowmath_120_180_state2,
            rows = rainbowmath_120_180_rows,
            columns = rainbowmath_120_180_cols,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times
        without smoke coming out of the machine.
        """
        gol = gollyx_python.StarGOLGenerations(
            s1 = rainbowmath_120_180_state1,
            s2 = rainbowmath_120_180_state2,
            rows = rainbowmath_120_180_rows,
            columns = rainbowmath_120_180_cols,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )
        for i in range(5):
            gol.next_step()

    def test_rainbowmath_120_180_finegrained(self):
        """
        Check the actual results of steps against known good results from JS simulator
        """
        gol = gollyx_python.StarGOLGenerations(
            s1 = rainbowmath_120_180_state1,
            s2 = rainbowmath_120_180_state2,
            rows = rainbowmath_120_180_rows,
            columns = rainbowmath_120_180_cols,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )
        live_counts = gol.count()

        gold = rainbowmath_120_180_finegrained_gold
        for gold_generation, gold_color1, gold_color2, gold_color3 in gold:
            try:
                self.assertEqual(live_counts['generation'], gold_generation)
                self.assertEqual(live_counts['liveCellsColors'][0], gold_color1)
                self.assertEqual(live_counts['liveCellsColors'][1], gold_color2)
                self.assertEqual(live_counts['liveCellsColors'][2], gold_color3)
            except AssertionError:
                err = "Error: did not match counts on generation {gold_generation}"
                err += "\ngold 1, 2: {gold_color1} , {gold_color2}"
                err += "\ncalc 1, 2: {live_counts['liveCellsColors'][0]} , {live_counts['liveCellsColors'][0]}"
                raise Exception(err)
            live_counts = gol.next_step()

    def test_random_100_120_halting(self):
        gol = gollyx_python.StarGOLGenerations(
            s1 = rainbowmath_120_180_state1,
            s2 = rainbowmath_120_180_state2,
            rows = rainbowmath_120_180_rows,
            columns = rainbowmath_120_180_cols,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )
        live_counts = gol.count()

        while gol.running and gol.generation < 1060:
            live_counts = gol.next_step()

        self.assertEqual(gol.generation, random_100_120_final[0])
        self.assertEqual(live_counts['liveCellsColors'][0], random_100_120_final[1])
        self.assertEqual(live_counts['liveCellsColors'][1], random_100_120_final[2])
        self.assertEqual(live_counts['liveCellsColors'][2], random_100_120_final[3])

