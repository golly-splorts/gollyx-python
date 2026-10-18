from gollyx_python import run_simulation
import unittest
from .fixtures_outcomes import OUTCOMES


class OutcomesTest(unittest.TestCase):

    def test_outcomes(self):
        """
        Check scores, generations, success and tie of each game against known good results
        """
        for game in OUTCOMES:
            with self.subTest(game=game["name"]):
                result = run_simulation(**game["kwargs"])
                self.assertEqual(result, game["expected"])
