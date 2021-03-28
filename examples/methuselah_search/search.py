import json
import itertools
import time
import re
import os
from pprint import pprint
from gollyx_python.manager import GOL


HERE = os.path.dirname(os.path.abspath(__file__))
results_file = os.path.join(HERE, 'results.json')


def coordinates_to_json(coordinates, xoffset=0, yoffset=0):
    """
    Convert a list of (x, y) tuples to a JSON list life dictionary
    (keys are string integers y, values are list of x values)
    """
    result = {}
    yvalues = sorted([j[1]+yoffset for j in coordinates])
    for y in yvalues:
        ystr = str(y)
        xvalues = sorted([j[0]+xoffset for j in coordinates if j[1]+yoffset==y])
        result[ystr] = xvalues
    s = json.dumps([result])
    s = re.sub(' ','', s)
    return s


def generate_methuselah_candidates(n_alive_cells, w, h, xoffset=0, yoffset=0):
    # Generates grid coordinates using itertools
    for indices_1d in itertools.combinations(range(0,w*h), n_alive_cells):
        points_list = []
        for ix_1d in indices_1d:
            irow = ix_1d//w
            icol = ix_1d%w
            points_list.append((irow, icol))
        yield coordinates_to_json(points_list, xoffset, yoffset)


def check_for_methuselah():
    rule_b = [3, 5, 7]
    rule_s = [2, 3, 8]
    s1, s2 = generate_methuselah_candidate()
    gol = GOL(
        s1=s1,
        s2=s2,
        rows=100,
        columns=120,
        rule_b=rule_b,
        rule_s=rule_s,
        halt=False,
        neighbor_color_legacy_mode=False,
    )


def record_methuselah_outcome(candidate, outcome):
    with open(results_file, 'r') as f:
        results = json.load(f)
    results[candidate] = outcome
    with open(results_file, 'w') as f:
        json.dump(results, f)


def main():
    coordinate_generator = generate_methuselah_candidates(3, 3, 3, xoffset=30, yoffset=30)
    for coordinates_json in coordinate_generator:
        #check_for_methuselah(coordinates_json)
        print('http://192.168.30.20:8888/simulator/index.html?s1=' + coordinates_json)



if __name__ == "__main__":
    main()
