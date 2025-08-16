import gollyx_python
import unittest


class ToroidalTest(unittest.TestCase):
    STATE1 = '[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]'
    STATE2 = '[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]'
    ROWS = 120
    COLS = 100

    def test_constructor(self):
        rule_b = [3]
        rule_s = [2, 3]

        gollyx_python.ToroidalGOL(
            s1=self.STATE1,
            s2=self.STATE2,
            rows=self.ROWS,
            columns=self.COLS,
            rule_b=rule_b,
            rule_s=rule_s,
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times without errors
        """
        rule_b = [3]
        rule_s = [2, 3]

        gol = gollyx_python.ToroidalGOL(
            s1='[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
            s2='[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
            rows=100,
            columns=120,
            rule_b=rule_b,
            rule_s=rule_s,
        )
        for i in range(20):
            gol.next_step()

    def test_periodic_life_100_120(self):
        """
        Check the actual results of the calculations against known good results
        """
        gol = gollyx_python.ToroidalGOL(
            s1='[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
            s2='[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
            rows=100,
            columns=120,
            periodic=True,
        )
        live_counts = gol.count()
        self.assertEqual(live_counts["generation"], 0)
        self.assertEqual(live_counts["liveCells1"], 7)
        self.assertEqual(live_counts["liveCells2"], 7)

        # Take 10 steps, check results
        for i in range(10):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 10)
        self.assertEqual(live_counts["liveCells1"], 30)
        self.assertEqual(live_counts["liveCells2"], 30)

        # Take 20 steps, check results
        for i in range(10):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 20)
        self.assertEqual(live_counts["liveCells1"], 32)
        self.assertEqual(live_counts["liveCells2"], 32)

        # Take 100 steps, check results
        for i in range(80):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 100)
        self.assertEqual(live_counts["liveCells1"], 76)
        self.assertEqual(live_counts["liveCells2"], 76)

        # Now do 420
        for i in range(320):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 420)
        self.assertEqual(live_counts["liveCells1"], 299)
        self.assertEqual(live_counts["liveCells2"], 450)

        # Last we do 1001
        for i in range(581):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 1001)
        self.assertEqual(live_counts["liveCells1"], 64)
        self.assertEqual(live_counts["liveCells2"], 382)

    def test_life_150_240_stoppingcriteria_280(self):
        rule_b = [3]
        rule_s = [2, 3]

        gol = gollyx_python.ToroidalGOL(
            s1='[{"30":[50,51,54,55,56]},{"31":[53]},{"32":[51]}]',
            s2='[{"90":[25]},{"91":[27]},{"92":[24,25,28,29,30]}]',
            rows=150,
            columns=240,
            rule_b=rule_b,
            rule_s=rule_s,
            maxdim=280,
            periodic=True,
        )
        live_counts = gol.count()

        self.assertEqual(live_counts["generation"], 0)
        self.assertEqual(live_counts["liveCells"],  14)
        self.assertEqual(live_counts["liveCells1"], 7)
        self.assertEqual(live_counts["liveCells2"], 7)

        # Take 60 steps, check results
        for i in range(60):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 60)
        self.assertEqual(live_counts["liveCells"],  156)
        self.assertEqual(live_counts["liveCells1"], 78)
        self.assertEqual(live_counts["liveCells2"], 78)
        print("Passed 60 steps check")

        # Take 80 steps, check results
        for i in range(20):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 80)
        self.assertEqual(live_counts["liveCells"],  190)
        self.assertEqual(live_counts["liveCells1"], 95)
        self.assertEqual(live_counts["liveCells2"], 95)
        print("Passed 80 steps check")

        # ----------

        # Take 100 steps, check results
        for i in range(20):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 100)
        self.assertEqual(live_counts["liveCells"],  152)
        self.assertEqual(live_counts["liveCells1"], 76)
        self.assertEqual(live_counts["liveCells2"], 76)
        print("Passed 10 steps check")

        # Take 500 steps, check results
        for i in range(400):
            live_counts = gol.next_step()

        self.assertEqual(live_counts["generation"], 500)
        self.assertEqual(live_counts["liveCells"],  678)
        self.assertEqual(live_counts["liveCells1"], 207)
        self.assertEqual(live_counts["liveCells2"], 471)

        # Stops after 3364 generations
        while gol.running and gol.generation < 3368:
            live_counts = gol.next_step()

        # Should stop right at 3364
        self.assertEqual(gol.generation, 3364)
        self.assertEqual(live_counts["liveCells"],  689)
        self.assertEqual(live_counts["liveCells1"], 132)
        self.assertEqual(live_counts["liveCells2"], 557)

