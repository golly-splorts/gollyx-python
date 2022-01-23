from gollyx_python import HellmouthGOL

def main():
    gol = HellmouthGOL(
        s1 = '[{"49":[176,177,180,181,182]},{"50":[179]},{"51":[177]}]',
        s2 = '[{"149":[114]},{"150":[116]},{"151":[113,114,117,118,119]}]',
        rows=200,
        columns=240,
    )

    while gol.running:
        live_counts = gol.next_step()
        if gol.generation%500==0:
            print(f"Simulating generation {gol.generation}")
            print(gol.count())

    from pprint import pprint
    pprint(gol.count())

if __name__=="__main__":
    main()
