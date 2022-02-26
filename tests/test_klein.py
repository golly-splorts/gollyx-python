import gollyx_python
import unittest
from .fixtures_klein import (
    random_200_100_state1,
    random_200_100_state2,
    random_200_100_finegrained_gold,
    random_200_100_final,
)


class KleinTest(unittest.TestCase):

    klein_b = [3]
    klein_s = [2, 3]

    def test_constructor(self):
        """
        Test that we can successfully construct a Generations CA
        """
        gollyx_python.KleinGOL(
            s1=random_200_100_state1,
            s2=random_200_100_state2,
            rows=100,
            columns=200,
            rule_b=self.klein_b,
            rule_s=self.klein_s,
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times
        without smoke coming out of the machine.
        """
        gol = gollyx_python.KleinGOL(
            s1=random_200_100_state1,
            s2=random_200_100_state2,
            rows=100,
            columns=200,
            rule_b=self.klein_b,
            rule_s=self.klein_s,
        )
        for i in range(5):
            gol.next_step()

    def test_random_200_100_finegrained(self):

        gol = gollyx_python.KleinGOL(
            s1=random_200_100_state1,
            s2=random_200_100_state2,
            rows=100,
            columns=200,
            rule_b=self.klein_b,
            rule_s=self.klein_s,
        )

        live_counts = gol.count()

        gold = random_200_100_finegrained_gold
        for gold_generation, gold_color1, gold_color2 in gold:
            try:
                self.assertEqual(live_counts['generation'], gold_generation)
                self.assertEqual(live_counts['liveCells'], gold_color1+gold_color2)
                self.assertEqual(live_counts['liveCells1'], gold_color1)
                self.assertEqual(live_counts['liveCells2'], gold_color2)
            except AssertionError:
                import pdb; pdb.set_trace()
                err = f"Error: did not match counts on generation {gold_generation}"
                err += f"\ngold 1, 2: {gold_color1} , {gold_color2}"
                err += f"\ncalc 1, 2: {live_counts['liveCells1']} , {live_counts['liveCells2']}"
                raise Exception(err)
            live_counts = gol.next_step()

    def test_random_200_100_halting(self):

        gol = gollyx_python.KleinGOL(
            s1=random_200_100_state1,
            s2=random_200_100_state2,
            rows=100,
            columns=200,
            rule_b=self.klein_b,
            rule_s=self.klein_s,
        )
        live_counts = gol.count()

        while gol.running and gol.generation < 7725:
            live_counts = gol.next_step()

        self.assertEqual(gol.generation, random_200_100_final[0])
        self.assertEqual(live_counts['liveCells1'], random_200_100_final[1])
        self.assertEqual(live_counts['liveCells2'], random_200_100_final[2])


