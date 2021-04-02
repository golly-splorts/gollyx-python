from .constants import SMOL, MAXDIM, EQUALTOL
from .utils import approx_equal
from .movingavglist import MovingAvgList


class LifeStats(object):
    """
    Object to hold statistical information about a Life object.
    This abstraction is messy, since the Life object creates LifeStats,
    but LifeStats still requires up-to-date information about the Life object,
    and changes the Life object when a victor is found.
    """
    livecells = 0
    livecells1 = 0
    livecells2 = 0
    victory = 0.0
    who_won = 0
    coverage = 0.0
    territory1 = 0.0
    territory2 = 0.0

    found_victor: bool = False

    running_avg_window: MovingAvgList
    running_avg_last3: MovingAvgList

    def __init__(self, life):
        self.running_avg_window = [
            0.0,
        ] * MAXDIM
        self.life = life
        self.rows = life.rows
        self.columns = life.columns
        self.running_avg_window = MovingAvgList()
        self.running_avg_last3 = MovingAvgList()
        self.found_victor = False

    def get_live_counts(self, state, state1, state2, generation):

        livecells = self.livecells = state.count_live_cells()
        livecells1 = self.livecells1 = state1.count_live_cells()
        livecells2 = self.livecells2 = state2.count_live_cells()

        victory = 0.0
        if livecells1 > livecells2:
            victory = (livecells1 / (1.0 * livecells1 + livecells2 + SMOL)) * 100
        else:
            victory = (livecells2 / (1.0 * livecells1 + livecells2 + SMOL)) * 100
        self.victory = victory
        total_area = self.columns * self.rows

        coverage = self.coverage = (livecells / (1.0 * total_area)) * 100
        territory1 = self.territory1 = (livecells1 / (1.0 * total_area)) * 100
        territory2 = self.territory2 = (livecells2 / (1.0 * total_area)) * 100

        return dict(
            generation=generation,
            liveCells=livecells,
            liveCells1=livecells1,
            liveCells2=livecells2,
            victoryPct=victory,
            coverage=coverage,
            territory1=territory1,
            territory2=territory2,
        )

    def update_moving_avg(self):
        if not self.found_victor:
            if self.life.generation < MAXDIM:
                self.running_avg_window.push_back(self.victory)
            else:
                # pop front push back
                self.running_avg_window.push_back_pop_front(self.victory)
                running_avg = self.running_avg_window.avg()

                if self.running_avg_last3.length() < 3:
                    self.running_avg_last3.push_back(running_avg)
                    removed = 0
                else:
                    removed = self.running_avg_last3.push_back_pop_front(running_avg)

                tol = EQUALTOL
                # Skip the first few steps where we're removing zeros
                if not approx_equal(removed, 0.0, tol):
                    b1 = approx_equal(
                        self.running_avg_last3.index(0), self.running_avg_last3.index(1), tol
                    )
                    b2 = approx_equal(
                        self.running_avg_last3.index(1), self.running_avg_last3.index(2), tol
                    )
                    zerocells = self.livecells1 == 0 or self.livecells2 == 0
                    if (b1 and b2) or zerocells:
                        z1 = approx_equal(self.running_avg_last3.index(0), 50.0, tol)
                        z2 = approx_equal(self.running_avg_last3.index(1), 50.0, tol)
                        z3 = approx_equal(self.running_avg_last3.index(2), 50.0, tol)
                        if (not (z1 or z2 or z3)) or zerocells:
                            # Declare victory in the life object
                            if self.livecells1 > self.livecells2:
                                self.found_victor = True
                                self.who_won = 1
                            elif self.livecells1 < self.livecells2:
                                self.found_victor = True
                                self.who_won = 2
