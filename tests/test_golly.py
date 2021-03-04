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

    def test_life_100_120(self):
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
        self.assertEqual(live_counts['generation'], 0)
        self.assertEqual(live_counts['liveCells1'], 7)
        self.assertEqual(live_counts['liveCells2'], 7)

        # Take 10 steps, check results
        for i in range(10):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 10)
        self.assertEqual(live_counts['liveCells1'], 30)
        self.assertEqual(live_counts['liveCells2'], 30)

        # Take 20 steps, check results
        for i in range(10):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 20)
        self.assertEqual(live_counts['liveCells1'], 32)
        self.assertEqual(live_counts['liveCells2'], 32)

        # Take 100 steps, check results
        for i in range(80):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 100)
        self.assertEqual(live_counts['liveCells1'], 76)
        self.assertEqual(live_counts['liveCells2'], 35)

        # Now do 420
        for i in range(320):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 420)
        self.assertEqual(live_counts['liveCells1'], 241)
        self.assertEqual(live_counts['liveCells2'], 115)

        # Last we do 1001
        for i in range(581):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 1001)
        self.assertEqual(live_counts['liveCells1'], 248)
        self.assertEqual(live_counts['liveCells2'], 50)

    def test_life_200_240(self):
        gol = golly_python.pylife.GOL(
            s1 = '[{"49":[176,177,180,181,182]},{"50":[179]},{"51":[177]}]',
            s2 = '[{"149":[114]},{"150":[116]},{"151":[113,114,117,118,119]}]',
            rows=200,
            columns=240,
        )
        live_counts = gol.get_live_counts()
        self.assertEqual(live_counts['liveCells1'], 7)
        self.assertEqual(live_counts['liveCells2'], 7)

        # Take 500 steps, check results
        for i in range(500):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 500)
        self.assertEqual(live_counts['liveCells'], 565)
        self.assertEqual(live_counts['liveCells1'], 267)
        self.assertEqual(live_counts['liveCells2'], 298)

        # Take 500 more steps, check results
        for i in range(500):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 1000)
        self.assertEqual(live_counts['liveCells'], 857)
        self.assertEqual(live_counts['liveCells1'], 403)
        self.assertEqual(live_counts['liveCells2'], 454)

        # Take 500 more steps, check results
        for i in range(500):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 1500)
        self.assertEqual(live_counts['liveCells'], 696)
        self.assertEqual(live_counts['liveCells1'], 338)
        self.assertEqual(live_counts['liveCells2'], 358)

        # Take 500 more steps, check results
        for i in range(500):
            live_counts = gol.next_step()

        self.assertEqual(live_counts['generation'], 2000)
        self.assertEqual(live_counts['liveCells'], 617)
        self.assertEqual(live_counts['liveCells1'], 262)
        self.assertEqual(live_counts['liveCells2'], 355)
