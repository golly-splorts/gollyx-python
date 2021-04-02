import subprocess
import json
import itertools
import time
import re
import os
from pprint import pprint
from gollyx_python.manager import GOL


HERE = os.path.dirname(os.path.abspath(__file__))


def lists_equal(a, b):
    if len(a) != len(b):
        return False
    sa = sorted(a)
    sb = sorted(b)
    for ia, ib in zip(sa, sb):
        if ia != ib:
            return False
    return True


def all_elements_equal(a):
    for i in range(1, len(a)):
        if a[i] != a[i - 1]:
            return False
    return True


class Search(object):
    def __init__(self, n_alive_cells, w, h, xoffset, yoffset, ngens):
        self.n_alive_cells = n_alive_cells
        self.w = w
        self.h = h
        self.xoff = xoffset
        self.yoff = yoffset
        self.ngens = ngens

        self.results_file = os.path.join(
            HERE, "results_n%d_w%d_h%d.json" % (n_alive_cells, w, h)
        )
        self.resultsm1_file = os.path.join(
            HERE, "results_n%d_w%d_h%d.json" % (n_alive_cells - 1, w, h)
        )
        if os.path.exists(self.resultsm1_file):
            with open(self.resultsm1_file, "r") as f:
                self.resultsm1 = json.load(f)
        else:
            self.resultsm1 = {}
        self.results = {}

    def coordinates_to_json(self, coordinates, xoffset=0, yoffset=0):
        """
        Convert a list of (x, y) tuples to a JSON list life dictionary
        (keys are string integers y, values are list of x values)
        """
        result = {}
        yvalues = sorted([j[1] + yoffset for j in coordinates])
        for y in yvalues:
            ystr = str(y)
            xvalues = sorted(
                [j[0] + xoffset for j in coordinates if j[1] + yoffset == y]
            )
            result[ystr] = xvalues
        s = json.dumps([result])
        s = re.sub(" ", "", s)
        return s

    def is_invariant_rotation(self, points_list, xoffset, yoffset):

        results = self.results

        def _rot90(points_list):
            maxdim = max(
                max([j[0] for j in points_list]), max([j[1] for j in points_list])
            )
            new_points_list = []
            for x, y in points_list:
                new_points_list.append((maxdim - y - 1, x))
            return new_points_list

        def _hflip(points_list):
            maxx = max([j[0] for j in points_list])
            miny = min([j[1] for j in points_list])
            new_points_list = []
            for x, y in points_list:
                new_points_list.append((maxx - x, y - miny))
            return new_points_list

        def _vflip(points_list):
            minx = min([j[0] for j in points_list])
            maxy = max([j[1] for j in points_list])
            new_points_list = []
            for x, y in points_list:
                new_points_list.append((x - minx, maxy - y))
            return new_points_list

        def _normalize(points_list):
            xvalues = [j[0] for j in points_list]
            yvalues = [j[1] for j in points_list]
            new_points_list = []
            for (x, y) in points_list:
                new_points_list.append((x - min(xvalues), y - min(yvalues)))
            return new_points_list

        s = self.coordinates_to_json(points_list, xoffset, yoffset)
        if s in results.keys():
            return True

        sh = self.coordinates_to_json(_normalize(_hflip(points_list)), xoffset, yoffset)
        if sh in results.keys():
            return True

        sv = self.coordinates_to_json(_normalize(_vflip(points_list)), xoffset, yoffset)
        if sv in results.keys():
            return True

        shv = self.coordinates_to_json(
            _normalize(_hflip(_vflip(points_list))), xoffset, yoffset
        )
        if shv in results.keys():
            return True

        for nrots in range(1, 4):

            points_list_ = points_list[:]
            hpoints_list_ = _hflip(points_list[:])
            vpoints_list_ = _vflip(points_list[:])
            hvpoints_list_ = _hflip(_vflip(points_list[:]))
            for i in range(nrots):
                points_list_ = _rot90(points_list_)
                hpoints_list_ = _rot90(hpoints_list_)
                vpoints_list_ = _rot90(vpoints_list_)
                hvpoints_list_ = _rot90(hvpoints_list_)

            points_list_ = _normalize(points_list_)
            hpoints_list_ = _normalize(hpoints_list_)
            vpoints_list_ = _normalize(vpoints_list_)
            hvpoints_list_ = _normalize(hvpoints_list_)

            s = self.coordinates_to_json(points_list_, xoffset, yoffset)
            if s in results.keys():
                return True

            sh = self.coordinates_to_json(hpoints_list_, xoffset, yoffset)
            if sh in results.keys():
                return True

            sv = self.coordinates_to_json(vpoints_list_, xoffset, yoffset)
            if sv in results.keys():
                return True

            shv = self.coordinates_to_json(hvpoints_list_, xoffset, yoffset)
            if shv in results.keys():
                return True

        return False

    def generate_methuselah_candidates(self, n_alive_cells, w, h, xoffset=0, yoffset=0):

        # Generate grid coordinates using itertools
        for indices_1d in itertools.combinations(range(0, w * h), n_alive_cells):
            points_list = []
            for ix_1d in indices_1d:
                irow = ix_1d // w
                icol = ix_1d % w
                points_list.append((irow, icol))
            if not self.is_invariant_rotation(points_list, xoffset, yoffset):
                result = self.coordinates_to_json(points_list, xoffset, yoffset)
                yield result

    def check_for_methuselah(self, s1_json, n_alive_cells, ngens):
        rule_b = [3, 5, 7]
        rule_s = [2, 3, 8]

        gol = GOL(
            s1=s1_json,
            s2="[]",
            rows=100,
            columns=120,
            rule_b=rule_b,
            rule_s=rule_s,
            halt=False,
            neighbor_color_legacy_mode=False,
        )

        static_gens = 5
        window = [
            0,
        ] * static_gens
        stop_early = False
        for istep in range(50):
            livecounts = gol.next_step()

            if livecounts["liveCells1"] == 0:
                # died too early
                return False

            # Get state 1 as json
            blife = gol.life
            s1 = blife.actual_state1
            s1json = s1.statelist.serialize()

            if (livecounts["liveCells1"] == self.n_alive_cells - 1) and (
                s1json in self.resultsm1
            ):
                # We already dealt with this state
                break

            if istep < static_gens:
                # keep going
                window[istep] = livecounts["liveCells1"]
            else:
                # update the sliding window of live cell counts
                window = window[1:static_gens] + [livecounts["liveCells1"]]

                # check if number of cells has been the same for N generations
                if all_elements_equal(window):

                    # if we reached steady state, ensure it takes a while
                    if istep < ngens//10:
                        return False

                    # if we reached steady state, ensure have at least K times the original cells
                    K = 3
                    if livecounts["liveCells1"] <= K * n_alive_cells:
                        return False

        if stop_early:
            # We already reached a state we have seen before
            return False
        elif livecounts["liveCells1"] < n_alive_cells + 1:
            # We made it through 40 iterations without stopping
            # but not enough cells
            return False
        else:
            # We made it through 40 iterations without stopping
            # Yup, hello methuselah
            return True

    def main(self):
        n_alive_cells = self.n_alive_cells
        w = self.w
        h = self.h
        xoff = self.xoff
        yoff = self.yoff
        ngens = self.ngens

        if os.path.exists(self.results_file):
            with open(self.results_file, "r") as f:
                self.results = json.load(f)

        coordinate_generator = self.generate_methuselah_candidates(
            n_alive_cells, w, h, xoffset=xoff, yoffset=yoff
        )
        for coordinates_json in coordinate_generator:
            outcome = self.check_for_methuselah(coordinates_json, n_alive_cells, ngens)
            self.results[coordinates_json] = outcome
            if outcome:
                print(
                    "http://192.168.30.20:8888/simulator/index.html?s1="
                    + coordinates_json
                )
                # Only write to file every once and a while
                with open(self.results_file, "w") as f:
                    json.dump(self.results, f, indent=4)


if __name__ == "__main__":

    print("")
    print("=============================================")
    print("=========  working on 5-cell methuselahs ====")
    print("=============================================")

    s = Search(
        n_alive_cells=5,
        w=4,
        h=4,
        xoffset=30,
        yoffset=30,
        ngens=100
    )
    s.main()

    print("")
    print("=============================================")
    print("=========  working on 6-cell methuselahs ====")
    print("=============================================")

    s = Search(
        n_alive_cells=6,
        w=4,
        h=4,
        xoffset=30,
        yoffset=30,
        ngens=200
    )
    s.main()

    print("")
    print("=============================================")
    print("=========  working on 7-cell methuselahs ====")
    print("=============================================")

    s = Search(
        n_alive_cells=7,
        w=4,
        h=4,
        xoffset=30,
        yoffset=30,
        ngens=300
    )
    s.main()

    print("")
    print("=============================================")
    print("=========  working on 8-cell methuselahs ====")
    print("=============================================")

    s = Search(
        n_alive_cells=8,
        w=4,
        h=4,
        xoffset=30,
        yoffset=30,
        ngens=300
    )
    s.main()

    print("")
    print("=============================================")
    print("=========  working on 9-cell methuselahs ====")
    print("=============================================")

    s = Search(
        n_alive_cells=9,
        w=4,
        h=4,
        xoffset=30,
        yoffset=30,
        ngens=400
    )
    s.main()
