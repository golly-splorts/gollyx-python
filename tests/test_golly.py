import golly_python.pylife
import unittest

class GollyPythonTest(unittest.TestCase):
    STATE1 = '[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]'
    STATE2 = '[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]'
    ROWS = 120
    COLS = 100

    def test_constructor(self):
        golly_python.pylife.GOL(
            s1 = self.STATE1,
            s2 = self.STATE2,
            rows = self.ROWS,
            columns = self.COLS
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times without errors
        """
        gol = golly_python.pylife.GOL(
            s1 = '[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
            s2 = '[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
            rows = 100,
            columns = 120
        )
        for i in range(20):
            gol.next_step()

    def test_life(self):
        """
        Check the actual results of the calculations against known good results
        """
        gol = golly_python.pylife.GOL(
            s1 = '[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
            s2 = '[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
            rows = 100,
            columns = 120
        )
        live_counts = gol.get_live_counts()
        self.assertEqual(live_counts['liveCells1'], 7)
        self.assertEqual(live_counts['liveCells2'], 7)

        # Take 10 steps, check results
        for i in range(10):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['liveCells1'], 30)
        self.assertEqual(live_counts['liveCells2'], 30)

        # Take 20 steps, check results
        for i in range(10):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['liveCells1'], 32)
        self.assertEqual(live_counts['liveCells2'], 32)

        # Take 100 steps, check results
        for i in range(80):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['liveCells1'], 76)
        self.assertEqual(live_counts['liveCells2'], 35)

        # Now do 420
        for i in range(320):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['liveCells1'], 241)
        self.assertEqual(live_counts['liveCells2'], 115)

        # Last we do 1001
        for i in range(581):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['liveCells1'], 248)
        self.assertEqual(live_counts['liveCells2'], 50)
