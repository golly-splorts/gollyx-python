import gollyx_python
import unittest
from .fixtures_quad import (
    get_twoacorn_fourcolor_fixture,
    get_math_fourcolor_fixture,
    math_fourcolor_finegrained_gold,
)


class RainbowTest(unittest.TestCase):
    STATE1 = '[{"30":[90]}]'
    STATE2 = '[{"90":[90]}]'
    STATE3 = '[{"30":[30]}]'
    STATE4 = '[{"90":[30]}]'

    ROWS = 120
    COLS = 180

    def test_constructor(self):
        rule_b = [3]
        rule_s = [2, 3]

        gollyx_python.RainbowGOL(
            s1 = self.STATE1,
            s2 = self.STATE2,
            s3 = self.STATE3,
            s4 = self.STATE4,
            rows = self.ROWS,
            columns = self.COLS,
            rule_b=rule_b,
            rule_s=rule_s,
            nteams=4
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times without errors
        """
        rule_b = [3]
        rule_s = [2, 3]

        states = get_twoacorn_fourcolor_fixture()

        gol = gollyx_python.RainbowGOL(
            **states,
            rows = self.ROWS,
            columns = self.COLS,
            rule_b=rule_b,
            rule_s=rule_s,
            nteams=4
        )
        for i in range(20):
            gol.next_step()

    def test_math_120_180_halt_criteria(self):
        rule_b = [3]
        rule_s = [2, 3]

        states = get_twoacorn_fourcolor_fixture()

        gol = gollyx_python.RainbowGOL(
            **states,
            rows = self.ROWS,
            columns = self.COLS,
            rule_b=rule_b,
            rule_s=rule_s,
            nteams=4
        )
        live_counts = gol.count()

        while gol.running and gol.generation < 1200:
            lc = gol.next_step()

        self.assertEqual(lc['generation'], 1154)
        self.assertEqual(lc['liveCells'], 400)
        self.assertEqual(lc['liveCells1'], 67)
        self.assertEqual(lc['liveCells2'], 116)
        self.assertEqual(lc['liveCells3'], 168)
        self.assertEqual(lc['liveCells4'], 49)

    def test_math_120_180_finegrained(self):
        rule_b = [3]
        rule_s = [2, 3]

        states = get_math_fourcolor_fixture()

        gol = gollyx_python.RainbowGOL(
            **states,
            rows = self.ROWS,
            columns = self.COLS,
            rule_b=rule_b,
            rule_s=rule_s,
            nteams=4
        )
        lc = gol.count()

        for gen, tot, t1s, t2s, t3s, t4s in math_fourcolor_finegrained_gold:
            # Update to this generation
            while gol.generation != gen:
                lc = gol.next_step()
            self.assertEqual(lc['generation'], gen)
            self.assertEqual(lc['liveCells'], tot)
            self.assertEqual(lc['liveCells1'], t1s)
            self.assertEqual(lc['liveCells2'], t2s)
            self.assertEqual(lc['liveCells3'], t3s)
            self.assertEqual(lc['liveCells4'], t4s)

