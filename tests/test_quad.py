import gollyx_python
import unittest
from .fixtures import get_twoacorn_fourcolor_fixture,


class GollyXPythonTest(unittest.TestCase):
    STATE1 = '[{"30":[90]}]'
    STATE2 = '[{"90":[90]}]'
    STATE3 = '[{"30":[30]}]'
    STATE4 = '[{"90":[30]}]'

    ROWS = 120
    COLS = 180

    def test_constructor(self):
        rule_b = [3]
        rule_s = [2, 3]

        gollyx_python.GOL(
            s1 = self.STATE1,
            s2 = self.STATE2,
            rows = self.ROWS,
            columns = self.COLS,
            rule_b=rule_b,
            rule_s=rule_s,
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times without errors
        """
        rule_b = [3]
        rule_s = [2, 3]

        states = get_twoacorn_fourcolor_fixture
        kwargs = {}
        for i in range(len(states)):
            k = f"s{i+1}"
            v = states[i]
            kwargs[k] = v

        gol = gollyx_python.GOL(
            **kwargs,
            rows = self.ROWS,
            columns = self.COLUMNS,
            rule_b=rule_b,
            rule_s=rule_s,
        )
        for i in range(20):
            gol.next_step()

    def test_life_120_180_halt_criteria(self):
        rule_b = [3]
        rule_s = [2, 3]

        states = get_twoacorn_fourcolor_fixture
        kwargs = {}
        for i in range(len(states)):
            k = f"s{i+1}"
            v = states[i]
            kwargs[k] = v

        gol = gollyx_python.GOL(
            **kwargs,
            rows = self.ROWS,
            columns = self.COLUMNS,
            rule_b=rule_b,
            rule_s=rule_s,
        )
        live_counts = gol.count()

        while gol.running and gol.generation < 1200:
            live_counts = gol.next_step()

        self.assertEqual(lc['generation'], 1154)
        self.assertEqual(lc['liveCells'], 400)
        self.assertEqual(lc['liveCells1'], 67)
        self.assertEqual(lc['liveCells2'], 116)
        self.assertEqual(lc['liveCells3'], 168)
        self.assertEqual(lc['liveCells4'], 49)
