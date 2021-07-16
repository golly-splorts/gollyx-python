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
