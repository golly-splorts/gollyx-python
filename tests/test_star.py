import gollyx_python
import unittest
from .fixtures_star import (
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
    random_100_120_finegrained_gold,
    flying_v2_122_222_state1,
    flying_v2_122_222_state2,
)


class StarGenerationsTest(unittest.TestCase):

    star_wars_b = [2]
    star_wars_s = [3, 4, 5]
    star_wars_c = 4

    def test_constructor(self):
        """
        Test that we can successfully construct a Generations CA
        """
        gollyx_python.StarGOL(
            s1=rainbowmath_120_180_state1,
            s2=rainbowmath_120_180_state2,
            rows=rainbowmath_120_180_rows,
            columns=rainbowmath_120_180_cols,
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
        gol = gollyx_python.StarGOL(
            s1=rainbowmath_120_180_state1,
            s2=rainbowmath_120_180_state2,
            rows=rainbowmath_120_180_rows,
            columns=rainbowmath_120_180_cols,
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
        gol = gollyx_python.StarGOL(
            s1=rainbowmath_120_180_state1,
            s2=rainbowmath_120_180_state2,
            rows=rainbowmath_120_180_rows,
            columns=rainbowmath_120_180_cols,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )
        live_counts = gol.get_live_counts()

        gold = rainbowmath_120_180_finegrained_gold
        for gold_generation, gold_color1, gold_color2, gold_color3 in gold:
            try:
                self.assertEqual(live_counts['generation'], gold_generation)
                self.assertEqual(live_counts['liveCells1'], gold_color1)
                self.assertEqual(live_counts['liveCells2'], gold_color2)
                self.assertEqual(live_counts['liveCellsColors'][2], gold_color3)
                self.assertEqual(live_counts['liveCells'], gold_color1 + gold_color2 + gold_color3)
            except AssertionError:
                err =  f"Error: did not match counts on generation {gold_generation}"
                err += f"\ngold 1, 2, 3: {gold_color1}, {gold_color2}, {gold_color3}"
                err += f"\ncalc 1, 2, 3: {live_counts['liveCells1']}, {live_counts['liveCells2']}, {live_counts['liveCellsColors'][2]}"
                err += f"\ngold total: {gold_color1 + gold_color2 + gold_color3}"
                err += f"\ncalc total: {live_counts['liveCells']}"
                raise Exception(err)
            live_counts = gol.next_step()

    def test_random_100_120_halting(self):
        gol = gollyx_python.StarGOL(
            s1=random_100_120_state1,
            s2=random_100_120_state2,
            rows=random_100_120_rows,
            columns=random_100_120_cols,
            tol_zero=1e-8,
            tol_stable=1e-6,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )
        live_counts = gol.get_live_counts()

        while gol.running and gol.generation < 1060:
            live_counts = gol.next_step()

        self.assertEqual(gol.generation, random_100_120_final[0])
        self.assertEqual(live_counts['liveCells1'], random_100_120_final[1])
        self.assertEqual(live_counts['liveCells2'], random_100_120_final[2])
        self.assertEqual(live_counts['liveCellsColors'][2],  random_100_120_final[3])

    def test_random_100_120_finegrained(self):
        """
        Check the actual results of steps against known good results from JS simulator
        """
        gol = gollyx_python.StarGOL(
            s1=random_100_120_state1,
            s2=random_100_120_state2,
            rows=random_100_120_rows,
            columns=random_100_120_cols,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )
        live_counts = gol.get_live_counts()

        gold = random_100_120_finegrained_gold
        for gold_generation, gold_color1, gold_color2, gold_color3 in gold:
            try:
                self.assertEqual(live_counts['generation'], gold_generation)
                self.assertEqual(live_counts['liveCells1'], gold_color1)
                self.assertEqual(live_counts['liveCells2'], gold_color2)
                self.assertEqual(live_counts['liveCellsColors'][2], gold_color3)
                self.assertEqual(live_counts['liveCells'], gold_color1 + gold_color2 + gold_color3)
            except AssertionError:
                err =  f"Error: did not match counts on generation {gold_generation}"
                err += f"\ngold 1, 2, 3: {gold_color1}, {gold_color2}, {gold_color3}"
                err += f"\ncalc 1, 2, 3: {live_counts['liveCells1']}, {live_counts['liveCells2']}, {live_counts['liveCellsColors'][2]}"
                err += f"\ngold total: {gold_color1 + gold_color2 + gold_color3}"
                err += f"\ncalc total: {live_counts['liveCells']}"
                raise Exception(err)
            live_counts = gol.next_step()

    def test_flying_v2_122_222(self):
        gol = gollyx_python.StarGOL(
            s1=flying_v2_122_222_state1,
            s2=flying_v2_122_222_state2,
            rows=122,
            columns=222,
            rule_b=self.star_wars_b,
            rule_s=self.star_wars_s,
            rule_c=self.star_wars_c,
            periodic=True
        )
        live_counts = gol.get_live_counts()

        # Stop after 1138 generations
        while gol.running and gol.generation < 1140:
            live_counts = gol.next_step()

        # Should stop right at 1138
        self.assertEqual(gol.generation, 1138)
        self.assertEqual(live_counts["liveCells"],  87)
        self.assertEqual(live_counts["liveCells1"], 20)
        self.assertEqual(live_counts["liveCells2"], 67)