from pprint import pprint
import time
import json
from gollyx_python import GOL
from gollyx_maps import maps


def main():
    map_metadata = maps.get_all_map_metadata("rainbow", 0)
    pattern_names = [m["patternName"] for m in map_metadata]

    # print(pattern_names)

    pattern_name = "patiolights"

    nteams = 4
    rule_b = [3]
    rule_s = [2, 3]

    timeout_sec = 30*60

    rows = 120
    cols = 180

    m = maps.get_map_realization('rainbow', pattern_name, rows, cols)

    print("URL for map:")
    print(m['url'])

    kwargs = {}
    for i in range(nteams):
        state_key = f"initialConditions{i+1}"
        gol_key = f"s{i+1}"
        state = m[state_key]
        kwargs[gol_key] = state

    start = time.time()

    gol = GOL(
        **kwargs,
        rows=rows,
        columns=cols,
        rule_b=rule_b,
        rule_s=rule_s,
        nteams=nteams,
    )

    while gol.running:
        gol.next_step()
        if gol.generation % 1000 == 0:
            now = time.time()
            if (now - start) > timeout_sec:
                print(
                    f"Simulation @ {pattern_name} timed out! Last generation: {gol.generation}"
                )
                break
            if gol.generation > 25000:
                print(
                    f"Simulation @ {pattern_name} timed out at 25,000 generations!"
                )
                break
            print(
                f"Simulation @ {pattern_name} is on generation {gol.generation}!"
            )

    if gol.life.found_victor:
        # Double check that we didn't have a tie
        top_val = 0
        top_count = 0
        live_counts = gol.count()
        for i in range(nteams):
            live_key = f"liveCells{i+1}"
            live_val = live_counts[live_key]
            if live_val > top_val:
                top_val = live_val
                top_count = 1
            elif live_val == top_val:
                top_count += 1
        if top_val == 0:
            print(f"Simulation @ {pattern_name} had zero top score, would be restarting")
            # continue through
            lc = gol.get_live_counts()
            pprint(lc)
        elif top_count > 1:
            print(f"Simulation @ {pattern_name} was tied, would be restarting")
            # continue through
            lc = gol.get_live_counts()
            pprint(lc)
        elif top_val > 0 and top_count == 1:
            print(f"Simulation @ {pattern_name} simulation complete!")
            # done
        else:
            print(f"Simulation @ {pattern_name} would be restarting")
            # continue through
            lc = gol.get_live_counts()
            pprint(lc)
    else:
        print(f"Simulation @ {pattern_name} did not meet any halting criteria, would be restarting")
        # continue through
        lc = gol.get_live_counts()
        pprint(lc)

    lc = gol.get_live_counts()
    pprint(lc)


if __name__ == "__main__":
    main()
