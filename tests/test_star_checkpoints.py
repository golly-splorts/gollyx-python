from gollyx_python import StarGOL
import unittest
from .fixtures_star_checkpoints import STAR_CHECKPOINT_GAMES
from .star_digest import star_state_digest


class StarCheckpointsTest(unittest.TestCase):

    def test_star_checkpoints(self):
        """
        Check live counts and the full-state digest of each game at each checkpoint generation
        """
        for game in STAR_CHECKPOINT_GAMES:
            with self.subTest(game=game["name"]):
                gol = StarGOL(**game["kwargs"])
                gol.halt = False
                checkpoints = game["checkpoints"]
                last = max(checkpoints)
                while True:
                    if gol.generation in checkpoints:
                        counts, digest = checkpoints[gol.generation]
                        self.assertEqual(
                            list(gol.get_live_counts()["liveCellsColors"]), counts,
                            f"counts at generation {gol.generation}",
                        )
                        self.assertEqual(star_state_digest(gol), digest, f"digest at generation {gol.generation}")
                    if gol.generation >= last:
                        break
                    gol.next_step()
