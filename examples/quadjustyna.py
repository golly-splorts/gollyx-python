import time
from pprint import pprint
#from gollyx_python.pylife import GOL
from gollyx_python.manager import GOL


s1 = '[{"18":[50]},{"19":[49,50]},{"29":[39]},{"30":[39]},{"31":[39]},{"34":[54]},{"35":[52,53,55]},{"36":[48,49,50,53]},{"37":[40,53,54]},{"38":[40,52]},{"39":[40]},{"60":[64]},{"61":[63,64]},{"71":[53]},{"72":[53]},{"73":[53]},{"76":[68]},{"77":[66,67,69]},{"78":[62,63,64,67]},{"79":[54,67,68]},{"80":[54,66]},{"81":[54]}]'
s2 = '[{"21":[75]},{"22":[75,87]},{"23":[75,88,89]},{"24":[83,84,85,88]},{"25":[87,88,90]},{"26":[89]},{"29":[74]},{"30":[74]},{"31":[74]},{"41":[84,85]},{"42":[85]},{"58":[78]},{"59":[78,79]},{"69":[89]},{"70":[89]},{"71":[89]},{"74":[74]},{"75":[73,75,76]},{"76":[75,78,79,80]},{"77":[74,75,88]},{"78":[76,88]},{"79":[88]}]'

#s1 = '[{"50":[50, 51, 52]}]'
#s2 = '[{"70":[70, 71, 72]}]'


def main():
    gol = GOL(
        s1 = s1,
        s2 = s2,
        rows = 100,
        columns = 120,
        neighbor_color_legacy_mode = False
    )

    print("NOTE: This simulations should stop at generation 1305.")
    while gol.running:
        live_counts = gol.next_step()
        if gol.generation % 100 == 0:
            print(f"Generation {gol.generation}")
            pprint(gol.count())

    print("Should be 1305:")
    print(gol.generation)
    print(live_counts)


if __name__=="__main__":
    main()
