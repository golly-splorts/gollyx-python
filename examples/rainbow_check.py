from gollyx_python.pylife4 import QuaternaryLife
import json


def main():
    ics = [
        '[{"50":[60,160]},{"51":[62,162]},{"52":[59,60,63,64,65,159,160,163,164,165]}]',
        '[{"60":[60,160]},{"61":[62,162]},{"62":[59,60,63,64,65,159,160,163,164,165]}]',
        '[{"31":[29,30,33,34,35,129,130,133,134,135]},{"32":[32,132]},{"33":[30,130]}]',
        '[{"61":[29,30,33,34,35,129,130,133,134,135]},{"62":[32,132]},{"63":[30,130]}]',
    ]
    states = [
        json.loads(ics[i]) for i in range(len(ics))
    ]
    gol = QuaternaryLife(
        *states,
        rows=120,
        columns=180,
    )

    while gol.running:
        gol.next_step()
        if gol.generation % 500 == 0:
            print(f"Simulating generation {gol.generation}")

    from pprint import pprint

    lc = gol.get_live_counts()
    pprint(lc)

    assert lc['generation']==1154
    assert lc['liveCells']==400
    assert lc['liveCells1']==67
    assert lc['liveCells2']==116
    assert lc['liveCells3']==168
    assert lc['liveCells4']==49


if __name__ == "__main__":
    main()
