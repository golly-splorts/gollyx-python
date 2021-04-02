import json
import glob


for json_file in glob.glob('*n8_w4_h4*json'):
    print("")
    print("---------------------------")
    print(f'Opening json file: {json_file}')
    with open(json_file, 'r') as f:
        d = json.load(f)
    print("\n".join(['http://192.168.30.20:8888/simulator/index.html?s1='+j for j in d.keys() if d[j] is True]))
