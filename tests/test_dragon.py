import gollyx_python
import unittest
from .fixtures import (
    get_towers_fixture,
    get_rule30,
    get_rule60,
)


class GollyXDragonTest(unittest.TestCase):
    ROWS = 500
    COLS = 200

    def test_constructor(self):
        state1 = '[{"1":[2]}]'
        state2 = '[{"2":[4]}]'
        rulestr = get_rule30()
        gollyx_python.CA(
            s1 = state1,
            s2 = state2,
            rule = rulestr,
            rows = self.ROWS,
            columns = self.COLS,
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times without errors
        """
        state1 = '[{"1":[2]}]'
        state2 = '[{"2":[4]}]'
        rulestr = get_rule30()
        ca = gollyx_python.CA(
            s1 = state1,
            s2 = state2,
            rule = rulestr,
            rows = self.ROWS,
            columns = self.COLS,
        )
        for i in range(20):
            ca.next_step()

    def test_finegrained_200x500(self):
        pass

    def test_longrunning_200x500(self):
        pass

    def test_halt_criteria(self):
        cols = 200
        rows = 500
        state1, state2 = get_towers_fixture()
        rulestr = get_rule30()
        ca = gollyx_python.CA(
            s1 = state1,
            s2 = state2,
            rule = rulestr,
            rows = rows,
            columns = cols,
        )

        live_counts = ca.count()
        self.assertEqual(ca.generation, 0)
        self.assertEqual(live_counts['liveCells'], 2)
        self.assertEqual(live_counts['liveCells1'], 1)
        self.assertEqual(live_counts['liveCells2'], 1)

        live_counts = ca.next_step()
        self.assertEqual(ca.generation, 1)
        self.assertEqual(live_counts['liveCells'], 8)
        self.assertEqual(live_counts['liveCells1'], 4)
        self.assertEqual(live_counts['liveCells2'], 4)

        while ca.generation < 499:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 499)
        self.assertEqual(live_counts['liveCells'], 47257)
        self.assertEqual(live_counts['liveCells1'], 11493)
        self.assertEqual(live_counts['liveCells2'], 35764)
