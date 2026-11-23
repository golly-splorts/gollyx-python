import unittest
from gollyx_python import run_simulation
from .fixtures_outcomes import OUTCOMES


class MaxdimTest(unittest.TestCase):

    def test_maxdim_window(self):
        """
        Check that maxdim reaches the simulator: 280 matches the default, and a longer
        window changes when the game is declared stable
        """
        game = next(g for g in OUTCOMES if g["name"] == "vi-random")
        self.assertEqual(run_simulation(**game["kwargs"], maxdim=280), game["expected"])
        longer = run_simulation(**game["kwargs"], maxdim=350)
        self.assertNotEqual(longer["generations"], game["expected"]["generations"])
