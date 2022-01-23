import gollyx_python
import unittest
from .fixtures_dragon import (
    get_towers_fixture,
    get_minitowers_fixture,
    get_rule30,
    get_rule60,
)


class GollyXDragonTest(unittest.TestCase):
    def test_constructor(self):
        cols = 200
        rows = 500
        state1 = '[{"1":[2]}]'
        state2 = '[{"2":[4]}]'
        rulestr = get_rule30()
        gollyx_python.DragonCA(
            s1=state1,
            s2=state2,
            rule=rulestr,
            rows=rows,
            columns=cols,
        )

    def test_steps(self):
        """
        Check that we can step through the algorithm several times without errors
        """
        cols = 200
        rows = 500
        state1 = '[{"1":[2]}]'
        state2 = '[{"2":[4]}]'
        rulestr = get_rule30()
        ca = gollyx_python.DragonCA(
            s1=state1,
            s2=state2,
            rule=rulestr,
            rows=rows,
            columns=cols,
        )
        for i in range(20):
            ca.next_step()

    #########################################
    # Spot checks of long-running automata

    def test_longrunning_200x500_rule30(self):
        cols = 200
        rows = 500
        state1, state2 = get_towers_fixture()
        rulestr = get_rule30()
        ca = gollyx_python.DragonCA(
            s1=state1,
            s2=state2,
            rule=rulestr,
            rows=rows,
            columns=cols,
        )
        live_counts = ca.count()
        self.assertEqual(ca.generation, 0)
        self.assertEqual(live_counts["liveCells"], 2)
        self.assertEqual(live_counts["liveCells1"], 1)
        self.assertEqual(live_counts["liveCells2"], 1)

        while ca.generation < 100:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 100)
        self.assertEqual(live_counts["liveCells"], 7289)
        self.assertEqual(live_counts["liveCells1"], 2943)
        self.assertEqual(live_counts["liveCells2"], 4346)

        while ca.generation < 200:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 200)
        self.assertEqual(live_counts["liveCells"], 17240)
        self.assertEqual(live_counts["liveCells1"], 5529)
        self.assertEqual(live_counts["liveCells2"], 11711)

        while ca.generation < 300:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 300)
        self.assertEqual(live_counts["liveCells"], 27258)
        self.assertEqual(live_counts["liveCells1"], 7748)
        self.assertEqual(live_counts["liveCells2"], 19510)

        while ca.generation < 400:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 400)
        self.assertEqual(live_counts["liveCells"], 37324)
        self.assertEqual(live_counts["liveCells1"], 9868)
        self.assertEqual(live_counts["liveCells2"], 27456)

        while ca.generation < 499:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 499)
        self.assertEqual(live_counts["liveCells"], 47257)
        self.assertEqual(live_counts["liveCells1"], 11493)
        self.assertEqual(live_counts["liveCells2"], 35764)

    def test_longrunning_200x500_rule60(self):
        cols = 200
        rows = 500
        state1, state2 = get_towers_fixture()
        rulestr = get_rule60()
        ca = gollyx_python.DragonCA(
            s1=state1,
            s2=state2,
            rule=rulestr,
            rows=rows,
            columns=cols,
        )
        live_counts = ca.count()
        self.assertEqual(ca.generation, 0)
        self.assertEqual(live_counts["liveCells"], 2)
        self.assertEqual(live_counts["liveCells1"], 1)
        self.assertEqual(live_counts["liveCells2"], 1)

        while ca.generation < 100:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 100)
        self.assertEqual(live_counts["liveCells"], 1914)
        self.assertEqual(live_counts["liveCells1"], 959)
        self.assertEqual(live_counts["liveCells2"], 955)

        while ca.generation < 200:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 200)
        self.assertEqual(live_counts["liveCells"], 4182)
        self.assertEqual(live_counts["liveCells1"], 2105)
        self.assertEqual(live_counts["liveCells2"], 2077)

        while ca.generation < 300:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 300)
        self.assertEqual(live_counts["liveCells"], 6178)
        self.assertEqual(live_counts["liveCells1"], 3109)
        self.assertEqual(live_counts["liveCells2"], 3069)

        while ca.generation < 400:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 400)
        self.assertEqual(live_counts["liveCells"], 8410)
        self.assertEqual(live_counts["liveCells1"], 4235)
        self.assertEqual(live_counts["liveCells2"], 4175)

        while ca.generation < 499:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 499)
        self.assertEqual(live_counts["liveCells"], 10503)
        self.assertEqual(live_counts["liveCells1"], 5285)
        self.assertEqual(live_counts["liveCells2"], 5218)

    def test_longrunning_50x150_rule30(self):
        cols = 50
        rows = 150
        state1, state2 = get_minitowers_fixture()
        rulestr = get_rule30()
        ca = gollyx_python.DragonCA(
            s1=state1,
            s2=state2,
            rule=rulestr,
            rows=rows,
            columns=cols,
        )
        live_counts = ca.count()
        self.assertEqual(ca.generation, 0)
        self.assertEqual(live_counts["liveCells"], 2)
        self.assertEqual(live_counts["liveCells1"], 1)
        self.assertEqual(live_counts["liveCells2"], 1)

        while ca.generation < 50:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 50)
        self.assertEqual(live_counts["liveCells"], 1086)
        self.assertEqual(live_counts["liveCells1"], 340)
        self.assertEqual(live_counts["liveCells2"], 746)

        while ca.generation < 100:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 100)
        self.assertEqual(live_counts["liveCells"], 2366)
        self.assertEqual(live_counts["liveCells1"], 740)
        self.assertEqual(live_counts["liveCells2"], 1626)

        while ca.generation < 149:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 149)
        self.assertEqual(live_counts["liveCells"], 3609)
        self.assertEqual(live_counts["liveCells1"], 1132)
        self.assertEqual(live_counts["liveCells2"], 2477)

    def test_longrunning_50x150_rule60(self):
        cols = 50
        rows = 150
        state1, state2 = get_minitowers_fixture()
        rulestr = get_rule60()
        ca = gollyx_python.DragonCA(
            s1=state1,
            s2=state2,
            rule=rulestr,
            rows=rows,
            columns=cols,
        )
        live_counts = ca.count()
        self.assertEqual(ca.generation, 0)
        self.assertEqual(live_counts["liveCells"], 2)
        self.assertEqual(live_counts["liveCells1"], 1)
        self.assertEqual(live_counts["liveCells2"], 1)

        while ca.generation < 50:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 50)
        self.assertEqual(live_counts["liveCells"], 574)
        self.assertEqual(live_counts["liveCells1"], 283)
        self.assertEqual(live_counts["liveCells2"], 291)

        while ca.generation < 100:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 100)
        self.assertEqual(live_counts["liveCells"], 1140)
        self.assertEqual(live_counts["liveCells1"], 543)
        self.assertEqual(live_counts["liveCells2"], 597)

        while ca.generation < 149:
            live_counts = ca.next_step()

        self.assertEqual(ca.generation, 149)
        self.assertEqual(live_counts["liveCells"], 1710)
        self.assertEqual(live_counts["liveCells1"], 791)
        self.assertEqual(live_counts["liveCells2"], 919)

    def test_halt_criteria(self):
        cols = 200
        rows = 500
        state1, state2 = get_towers_fixture()
        rulestr = get_rule30()
        ca = gollyx_python.DragonCA(
            s1=state1,
            s2=state2,
            rule=rulestr,
            rows=rows,
            columns=cols,
        )

        live_counts = ca.count()
        self.assertEqual(ca.generation, 0)
        self.assertEqual(live_counts["liveCells"], 2)
        self.assertEqual(live_counts["liveCells1"], 1)
        self.assertEqual(live_counts["liveCells2"], 1)

        live_counts = ca.next_step()
        self.assertEqual(ca.generation, 1)
        self.assertEqual(live_counts["liveCells"], 8)
        self.assertEqual(live_counts["liveCells1"], 4)
        self.assertEqual(live_counts["liveCells2"], 4)

        while ca.running:
            live_counts = ca.next_step()
            if ca.generation > 750:
                # gonna fail
                break

        self.assertEqual(ca.generation, 499)
        self.assertEqual(live_counts["liveCells"], 47257)
        self.assertEqual(live_counts["liveCells1"], 11493)
        self.assertEqual(live_counts["liveCells2"], 35764)
