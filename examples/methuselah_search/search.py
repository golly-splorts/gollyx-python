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
    def __init__(self):
        self.results_file = os.path.join(HERE, "results.json")
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

            # [{"0":[0,1],"1":[0],"2":[0],"3":[0]}]
            # [{"0":[0],"1":[0],"2":[0],"3":[0,1]}]
            # z1 = [
            #    (0, 0),
            #    (1, 0),
            #    (0, 1),
            #    (0, 2),
            #    (0, 3)
            # ]
            # z2 = [
            #    (0, 0),
            #    (0, 1),
            #    (0, 2),
            #    (0, 3),
            #    (1, 3)
            # ]
            # if lists_equal(points_list, z2):
            #    import pdb; pdb.set_trace()
            #    a = 0
            if not self.is_invariant_rotation(points_list, xoffset, yoffset):
                result = self.coordinates_to_json(points_list, xoffset, yoffset)
                yield result

    def check_for_methuselah(self, s1_json, n_alive_cells):
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
        for istep in range(40):
            livecounts = gol.next_step()
            if livecounts["liveCells1"] == 0:
                # died too early
                return False
            if istep < static_gens:
                # keep going
                window[istep] = livecounts["liveCells1"]
            else:
                # check that pattern is not static for N generations
                window = window[1:static_gens] + [livecounts["liveCells1"]]
                if all_elements_equal(window):
                    if livecounts["liveCells1"] <= n_alive_cells + 8:
                        return False

        # We made it through 40 iterations without stopping
        # If we have enough cells in the end, this could be a methuselah
        if livecounts["liveCells1"] < n_alive_cells + 1:
            # Not enough cells
            return False
        else:
            # Yup, hello methuselah
            return True

    def main(self):
        n_alive_cells = 5
        w = 5
        h = 5

        if os.path.exists(self.results_file):
            with open(self.results_file, "r") as f:
                self.results = json.load(f)

        coordinate_generator = self.generate_methuselah_candidates(
            n_alive_cells, w, h, xoffset=0, yoffset=0
        )
        for coordinates_json in coordinate_generator:
            outcome = self.check_for_methuselah(coordinates_json, n_alive_cells)
            self.results[coordinates_json] = outcome
            if outcome:
                print(
                    "http://192.168.30.20:8888/simulator/index.html?s1="
                    + coordinates_json
                )
                with open(self.results_file, "w") as f:
                    json.dump(self.results, f, indent=4)


if __name__ == "__main__":
    s = Search()
    s.main()
