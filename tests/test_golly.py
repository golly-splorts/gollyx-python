import golly_python
import unittest

class GollyPythonTest(unittest.TestCase):
    STATE1 = '[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]'
    STATE2 = '[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]'
    ROWS = 120
    COLS = 100

    def test_constructor(self):
        golly_python.GOL(
            s1 = self.STATE1,
            s2 = self.STATE2,
            rows = self.ROWS,
            columns = self.COLS
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times without errors
        """
        gol = golly_python.GOL(
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
        gol = golly_python.GOL(
            s1 = '[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
            s2 = '[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
            rows = 100,
            columns = 120
        )
        live_counts = gol.count()

        gold = [
            [0, 7, 7],
            [1, 8, 8],
            [2, 10, 10],
            [3, 11, 11],
            [4, 11, 11],
            [5, 13, 13],
            [6, 15, 15],
            [7, 15, 15],
            [8, 18, 18],
            [9, 20, 20],
            [10, 30, 30],
            [11, 19, 19],
            [12, 14, 14],
            [13, 17, 17],
            [14, 20, 20],
            [15, 24, 24],
            [16, 28, 28],
            [17, 28, 28],
            [18, 25, 25],
            [19, 29, 29],
            [20, 32, 32],
            [21, 42, 42],
            [22, 38, 38],
            [23, 47, 47],
            [24, 52, 52],
            [25, 40, 40],
            [26, 34, 34],
            [27, 41, 41],
            [28, 42, 42],
            [29, 49, 49],
            [30, 57, 57],
            [31, 58, 58],
            [32, 50, 50],
            [33, 64, 64],
            [34, 63, 63],
            [35, 73, 73],
            [36, 68, 68],
            [37, 78, 78],
            [38, 92, 92],
            [39, 96, 96],
            [40, 96, 96],
            [41, 102, 102],
            [42, 92, 92],
            [43, 66, 66],
            [44, 67, 67],
            [45, 63, 63],
            [46, 68, 68],
            [47, 64, 64],
            [48, 73, 73],
            [49, 66, 66],
            [50, 96, 96],
            [51, 66, 66],
            [52, 69, 69],
            [53, 66, 66],
            [54, 66, 66],
            [55, 67, 67],
            [56, 62, 62],
            [57, 64, 64],
            [58, 71, 71],
            [59, 73, 73],
            [60, 78, 78],
            [61, 72, 72],
            [62, 78, 78],
            [63, 73, 73],
            [64, 83, 83],
            [65, 88, 88],
            [66, 85, 85],
            [67, 82, 82],
            [68, 83, 83],
            [69, 94, 94],
            [70, 94, 94],
            [71, 93, 93],
            [72, 100, 100],
            [73, 99, 99],
            [74, 87, 87],
            [75, 95, 95],
            [76, 81, 80],
            [77, 102, 99],
            [78, 96, 93],
            [79, 111, 107],
            [80, 95, 90],
            [81, 96, 89],
            [82, 100, 91],
            [83, 87, 77],
            [84, 84, 71],
            [85, 104, 90],
            [86, 85, 69],
            [87, 90, 71],
            [88, 85, 68],
            [89, 88, 62],
            [90, 84, 63],
            [91, 85, 54],
            [92, 77, 49],
            [93, 86, 49],
            [94, 84, 46],
            [95, 98, 44],
            [96, 76, 38],
            [97, 82, 33],
            [98, 73, 35],
            [99, 81, 32],
        ]

        for gold_generation, gold_color1, gold_color2 in gold:
            import pdb; pdb.set_trace()
            self.assertEqual(live_counts['generation'], gold_generation)
            self.assertEqual(live_counts['liveCells1'], gold_color1)
            self.assertEqual(live_counts['liveCells2'], gold_color2)
            live_counts = gol.next_step()

        ## Take 10 steps, check results
        #for i in range(10):
        #    live_counts = gol.next_step()

        #self.assertEqual(live_counts['generation'], 10)
        #self.assertEqual(live_counts['liveCells1'], 30)
        #self.assertEqual(live_counts['liveCells2'], 30)

        ## Take 20 steps, check results
        #for i in range(10):
        #    live_counts = gol.next_step()

        #self.assertEqual(live_counts['generation'], 20)
        #self.assertEqual(live_counts['liveCells1'], 32)
        #self.assertEqual(live_counts['liveCells2'], 32)

        ## Take 100 steps, check results
        #for i in range(80):
        #    live_counts = gol.next_step()

        #self.assertEqual(live_counts['generation'], 100)
        #self.assertEqual(live_counts['liveCells1'], 76)
        #self.assertEqual(live_counts['liveCells2'], 35)

        ## Now do 420
        #for i in range(320):
        #    live_counts = gol.next_step()

        #self.assertEqual(live_counts['generation'], 420)
        #self.assertEqual(live_counts['liveCells1'], 241)
        #self.assertEqual(live_counts['liveCells2'], 115)

        ## Last we do 1001
        #for i in range(581):
        #    live_counts = gol.next_step()

        #self.assertEqual(live_counts['generation'], 1001)
        #self.assertEqual(live_counts['liveCells1'], 248)
        #self.assertEqual(live_counts['liveCells2'], 50)

    def test_life_200_240(self):
        gol = golly_python.GOL(
            s1 = '[{"49":[176,177,180,181,182]},{"50":[179]},{"51":[177]}]',
            s2 = '[{"149":[114]},{"150":[116]},{"151":[113,114,117,118,119]}]',
            rows=200,
            columns=240,
        )
        live_counts = gol.count()
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
