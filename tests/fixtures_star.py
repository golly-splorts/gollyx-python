import json

# http://192.168.30.20:8888/index.html?s1=[{%220%22:[0,17,89,96,103,104,116]},{%221%22:[4,36,37,38,70,74,101,108]},{%222%22:[10,11,29,36,42,74,90,115,118]},{%223%22:[1,13,23,34,43,48,54,55,68,69,77,83]},{%224%22:[8,15,28,50,60,67,100]},{%225%22:[15,16,50,53,63,65,75,85,112,118]},{%226%22:[0,1,7,9,29,31,49,53,71,93,102,104]},{%227%22:[3,64,94,102,119]},{%228%22:[26,31,74,80,89,91,112,115]},{%229%22:[1,12,26,29,32,36,54,62,83,100,103]},{%2210%22:[46,57,74,103]},{%2211%22:[16,28,51]},{%2212%22:[10,13,23,33,65,79,119]},{%2213%22:[28,37,42,60,74,105]},{%2214%22:[19,24,41,63,93]},{%2215%22:[9,36,56,61,66,68,80,87,105,109,111]},{%2216%22:[5,12,21,26,37,39,55,62,82,88,96,98,112]},{%2217%22:[13,37,43,44,51,75,80,94,107,112,114]},{%2218%22:[2,21,30,36,44,46,63,70,71,73,81,84,95,109,111,119]},{%2219%22:[13,41,58,63,65,66,73,82,83,97,103,108]},{%2220%22:[16,25,41,63,79,116]},{%2221%22:[9,38,39,59,64,70,84]},{%2222%22:[3,5,32,33,65,106]},{%2223%22:[33,53,59,65,69,74,90,114]},{%2224%22:[2,48,58,61,64,66,90,91]},{%2225%22:[13,16,61,69,74,81,82,101,105,109]},{%2226%22:[20,28,46,47,53,68,73,84,85,93,94]},{%2227%22:[26,42,65,66,70,94,99,103,111]},{%2228%22:[6,12,71,81,97,103,113]},{%2229%22:[32,41,44,81,86,118]},{%2230%22:[27,35,40,48,98,100,117]},{%2231%22:[6,13,22,40,61,82,83,90,106]},{%2232%22:[37,43,50,92,105,112,115]},{%2233%22:[26,45,47,62,70,82,117]},{%2234%22:[3,6,17,19,27,36,58,62,85,92,106,112]},{%2235%22:[2,3,4,15,39,96]},{%2236%22:[2,5,9,14,31,32,36,73]},{%2237%22:[19,25,37,42,59,69,70,74,91]},{%2238%22:[4,25,55,57,65,68,88,117]},{%2239%22:[5,20,42,83,114]},{%2240%22:[17,46,64,87,91,105]},{%2241%22:[8,15,23,36,42,49,53,81,86,91,93,102,110,113]},{%2242%22:[2,4,31,38,52,66,83,98,116]},{%2243%22:[19,30,36,39,40,62,70,85,92,98,104]},{%2244%22:[9,21,58,71,89,95,96,106]},{%2245%22:[9,12,19,51,62,69,79]},{%2246%22:[1,22,33,37,57,68,70,74,90]},{%2247%22:[8,33,44,45,48,69,83,105,114]},{%2248%22:[4,9,42,44,46,57,68,92,102]},{%2249%22:[11,25,30,59,62,78,98]},{%2250%22:[8,22,33,57,91,95,96]},{%2251%22:[0,6,11,16,27,33,35,64,83,96]},{%2252%22:[5,39,55,66,83,85,87]},{%2253%22:[12,23,26,35,37,51,66,85,87,98,115]},{%2254%22:[15,28,63,79,84]},{%2255%22:[7,77,84,110,119]},{%2256%22:[19,37,41,59,61,62,73,92,110]},{%2257%22:[10,41,62,86]},{%2258%22:[1,49,108,109]},{%2259%22:[3,5,14,18,40,53,69,77,86,90]},{%2260%22:[18,26,37,43,87,90,98]},{%2261%22:[2,12,13,21,29,84,85,99,105,115]},{%2262%22:[4,30,39,61,78,104]},{%2263%22:[2,7,8,28,41,44,49,54,68,84,91,102]},{%2264%22:[12,14,25,29,30,36,38,54,67,93,104]},{%2265%22:[35,40,54,59,66,67,107,110,117]},{%2266%22:[4,7,11,55,90,97,105,114]},{%2267%22:[27,46,51,56,58,70,94,100]},{%2268%22:[32,45,46,48,62,84,86,87,97,110]},{%2269%22:[17,22,94,106]},{%2270%22:[13,26,67,79,110,119]},{%2271%22:[8,20,21,36,64,75,83,98,102,110,111]},{%2272%22:[11,23,38,40,81]},{%2273%22:[28,33,64,65,80,92,93]},{%2274%22:[23,42,53,58,90,97,106]},{%2275%22:[1,11,20,30,101,104,107,114]},{%2276%22:[6,7,28,35,47,67,73,94]},{%2277%22:[62,86,88,94,96,99,102]},{%2278%22:[20,40,64,76,79,80,82,92,109]},{%2279%22:[21,51]},{%2280%22:[63,94,103,107,114]},{%2281%22:[36,48,58,84,86,110]},{%2282%22:[47,48,56,76,80]},{%2283%22:[5,17,26,32,45,65,68,71,75,80]},{%2284%22:[42,87,119]},{%2285%22:[6,14,34,37,81,112]},{%2286%22:[4,7,31,51,70,72,86,100]},{%2287%22:[1,8,28,46,70,78,105,106]},{%2288%22:[27,36,56,88,101]},{%2289%22:[8,15,23,29,42,55,101]},{%2290%22:[19,34,51,66,74,80,96,105]},{%2291%22:[17,48,76,88,102,103,110]},{%2292%22:[4,6,11,16,64,109,119]},{%2293%22:[12,20,22,31,34,39,79,82,110]},{%2294%22:[23,27,43,49,70,83,100,106]},{%2295%22:[15,23,36]},{%2296%22:[0,4,74,86,100]},{%2297%22:[5,22,34,38,60,85,111,114,116]},{%2298%22:[88,97]},{%2299%22:[25,30,35,39,86,92,103,105,115,116]}]&s2=[{%220%22:[3,5,8,20,24,39,43,45,48,65,67,98]},{%221%22:[13,14,40,48,53,60,80,81,85]},{%222%22:[6,44,45,49,70,79,99,107,111]},{%223%22:[3,7,21,26,44,49,58,66,75,90,102,113]},{%224%22:[0,11,21,49,63,78,96]},{%225%22:[44,69,70]},{%226%22:[46,48,51,68,69,89,108]},{%227%22:[5,11,20,36,45,65,88,92,110,115]},{%228%22:[10,13,25,33,37,38,90,116]},{%229%22:[11,16,28,40,41,42,47,69,72,79,85,106,113]},{%2210%22:[7,30,60,70,95]},{%2211%22:[6,29,39,48,76,107,117]},{%2212%22:[0,7,9,12,21,36,68,76,100]},{%2213%22:[21,24,26,38,51,69,107,114,119]},{%2214%22:[10,12,33,55,95,96,115]},{%2215%22:[46,52,69,72,89]},{%2216%22:[2,17,30,33,38,49,102,108]},{%2217%22:[2,15,18,65,100]},{%2218%22:[27,35,59]},{%2219%22:[5,11,21,24,101]},{%2220%22:[3,7,15,21,53,62,80,82,83,85,109]},{%2221%22:[3,21,45,51,67,72,76,83,88]},{%2222%22:[30,45,76,78,79]},{%2223%22:[12,13,20,50,61,89,104,119]},{%2224%22:[25,60,65,70,100,103,105]},{%2225%22:[1,65,102,110]},{%2226%22:[3,15,27,75,107,114]},{%2227%22:[11,43]},{%2228%22:[1,8,20,32,40,47,48,56,107,109,112]},{%2229%22:[13,14,18,26,35,36,58,93,96,117]},{%2230%22:[7,13,29,31,55,73,79,92,102,110,113,116,119]},{%2231%22:[20,79,119]},{%2232%22:[19,46,52,56,80,89,100]},{%2233%22:[60,63,65,76,101,102,104,108]},{%2234%22:[0,4,5,11,15,18,28,43,46,87,97]},{%2235%22:[11,37,53,55,60,68,77,84,108]},{%2236%22:[3,13,16,35,48,58,60,62,68,77,84,86,88,90,93,97,112,119]},{%2237%22:[20,30,94,112]},{%2238%22:[39,41,71,93,102]},{%2239%22:[7,9,15,17,19,59,61,72,79,85,92]},{%2240%22:[0,14,29,39,47,56,71,85,103,109]},{%2241%22:[0,6,21,26,30,56,62,71,98,107]},{%2242%22:[25,35,47,86,89,96,97]},{%2243%22:[0,22,35,60,93,103]},{%2244%22:[10,23,33,37,47,53,57,67,68,72,99]},{%2245%22:[23,52,67,75,99,104,108,110]},{%2246%22:[16,40,43,60,81,83,98,102,105,109]},{%2247%22:[9,59,87,92]},{%2248%22:[0,3,10,24,60,72,82,87,88]},{%2249%22:[36,72,80,81,84,91,101,103]},{%2250%22:[2,20,30,45,46,59,63,79,81,84,89,108]},{%2251%22:[9,14,28,51,57,62,77,81,88,89,98,99,118]},{%2252%22:[9,19,42,69,96,102]},{%2253%22:[1,56,63,65,71,92,102,109]},{%2254%22:[10,17,18,35,53,56,80,91,95,101,116]},{%2255%22:[12,19,42,46,53,54,93]},{%2256%22:[8,12,34,43,53,77,90,105,109]},{%2257%22:[12,26,69,75,76,80,99,101,106]},{%2258%22:[2,34,36,39,86,107]},{%2259%22:[2,23,28,44,85,116]},{%2260%22:[25,28,35,55,73,103,105]},{%2261%22:[15,24,30,48,57,87,95,97,111]},{%2262%22:[27,67,77,88,90,101,112]},{%2263%22:[9,33,48,57,64,67,69,119]},{%2264%22:[6,18,47,74,75,97,112]},{%2265%22:[3,5,64,74,86,97,111,115]},{%2266%22:[1,32,40,47,54,64,67,69,72,104,107]},{%2267%22:[18,19,21,25,29]},{%2268%22:[3,21,22,30,40,54,66]},{%2269%22:[0,19,35,42,54,67,77,81,101]},{%2270%22:[12,46,50,106]},{%2271%22:[5,14,28,57,62,71,74,78,84,90]},{%2272%22:[2,13,17,47,63,84,97,106,114]},{%2273%22:[3,6,39,73,83,84,99,116,117]},{%2274%22:[8,47,65,67,82,87,92,108,110]},{%2275%22:[25,32,47,48,82,90,115]},{%2276%22:[9,21,38,43,53,75,83,91,92,95]},{%2277%22:[3,16,54,66,69,79,119]},{%2278%22:[37,65,84,102,106,118]},{%2279%22:[1,31,44,78,89,98]},{%2280%22:[8,10,13,18,33,79,81,93,115]},{%2281%22:[6,13,19,32,42,46,100,117]},{%2282%22:[24,46]},{%2283%22:[22,27,28,29,38,46,81,82,99,106,118]},{%2284%22:[7,38,48,74,86,108,110]},{%2285%22:[46,48,50,56,96,101]},{%2286%22:[1,16,21,47,84,88,91]},{%2287%22:[33,39,44,60,67,95,107,108,111]},{%2288%22:[53,108]},{%2289%22:[5,13,18,21,52,66,92]},{%2290%22:[0,9,42,59,63,69,89,92,94]},{%2291%22:[36,37,39,51,56,72,90,117,119]},{%2292%22:[9,28,101,104,110,117]},{%2293%22:[7,17,29,35,36,48,75,114,119]},{%2294%22:[21,52,53,68,82,116]},{%2295%22:[18,48,53,64,67,93,103]},{%2296%22:[8,9,11,14,41,49,65,89,109]},{%2297%22:[13,30,37,39,47,89,98]},{%2298%22:[7,10,49,50,77,89,105,109]},{%2299%22:[31,46]}]&rows=100&cols=120&cellSize=3

# ----------------
# Rainbow Math map, 120 x 180

rainbowmath_120_180_state1 = '[{"0":[16,41,51,66,86,111,121,126,136,141,146,156,176]},{"1":[16,26,46,61,81,91,111,141]},{"2":[16,21,76,101]},{"3":[16,21,41,71,86,101,151,161,166,171,176]},{"4":[31,66,81,106,116,121,126,136,161]},{"6":[0,13,17,18,19,38,42,47,69,77,79,82,83,92,93,102,118,139,142,144,153,164,169,173,177]},{"7":[16,26,96,106,116,156]},{"8":[11,46,61,66,136,171]},{"9":[6,11,16,26,46,76,86,91,111,116,121,136,141,146,156,161,166]},{"11":[2,4,8,9,12,18,23,24,29,32,33,34,37,38,39,47,52,58,59,64,68,69,93,108,113,118,119,127,128,129,133,139,143,148,158,162]},{"12":[41,81,91,111,136,141,161]},{"13":[41,46,96,106,116,146,151,176]},{"14":[16,31,36,61,76,81,91,121,126,146,151]},{"16":[2,12,24,34,43,53,54,58,59,64,79,84,109,117,124,128,132,139,144,147,152,153,157,167,172,174,179]},{"17":[6,21,101,106,121,126,166,176]},{"18":[26,41,71,156]},{"19":[11,61,76,141,146,176]},{"21":[0,3,28,44,53,59,79,84,87,88,92,94,99,109,114,117,119,132,153,167,169]},{"22":[36,61,71,121,126,131,176]},{"23":[11,16,86,111,141,156,166]},{"24":[41,56,66,121,131,161,166,176]},{"26":[1,4,17,28,29,38,49,59,68,74,77,82,83,92,93,94,112,118,122,124,127,129,133,137,139,144,152,153,154,162,163,169,172,179]},{"27":[21,31,46,61,91,96,106,116,131,146,176]},{"28":[6,11,31,56,71,96,126,156]},{"29":[6,51,76,86,106,121,126,131,136,141,166,176]},{"31":[0,1,2,7,24,27,33,47,53,89,102,108,112,113,124,127,129,134,147,152,157,159,163,167,173,174,179]},{"32":[16,101,111,121,126,131,141,156,171]},{"33":[26,31,116,161]},{"34":[21,26,36,41,66,101,121,146,156,166]},{"36":[12,18,22,23,32,34,39,44,47,53,63,73,74,78,83,103,107,108,109,118,122,123,134,137,148,157,167,178]},{"37":[11,16,66,86,111,126,131]},{"38":[51,66,81,86,151]},{"39":[21,26,46,91,106,121,126,156,171]},{"41":[2,4,7,9,17,19,29,34,38,39,42,49,72,74,83,89,99,108,112,119,122,128,129,133,137,139,142,164,178]},{"42":[11,46,56,61,71,76,81,126,136,161,171]},{"43":[11,26,36,56,121,146,161,171]},{"44":[6,16,51,66,71,76,126,136,146,151,156,171,176]},{"46":[0,1,4,7,9,18,19,24,28,34,38,42,44,47,62,64,67,73,77,78,93,97,98,103,108,112,118,132,139,147,148,152,167]},{"47":[11,31,71,141,166]},{"48":[31,61,71,76,91,101,121,146,176]},{"49":[31,71,86,91,111,116,121,136,141,146]},{"51":[1,3,12,38,39,48,54,64,67,82,92,93,94,99,123,137,142,143,149,157,162,168,173,177]},{"52":[26,46,51,61,101,106,121,151,161,166]},{"53":[16,41,61,76,106,141,161,171]},{"54":[11,26,31,56,61,66,76,96,151]},{"56":[2,8,9,44,47,49,58,62,69,79,88,97,104,112,118,119,128,134,138,144,147,149,152,157,167,168,172,173]},{"57":[6,36,56,66,71,81,101,126]},{"58":[6,26,56,61,66,71,111,116,141,146,156,166]},{"59":[31,41,61,66,86,111,116,121,141,151]},{"61":[0,2,3,4,7,14,17,18,23,32,38,64,68,72,83,84,93,118,119,124,128,133,134,148,149,159,163,172,174,177,179]},{"62":[16,31,46,111,121,136,146]},{"63":[26,31,46,61,86,91,101,106,116,156]},{"64":[46,81,106,111,121,146,156]},{"66":[3,8,9,14,19,47,59,72,74,77,84,87,89,92,104,107,118,124,143,153,158,179]},{"67":[6,21,51,61,91,96,106,111,131,141,146]},{"68":[6,26,56,61]},{"69":[6,46,56,91,116,131,141,166,176]},{"71":[0,1,2,3,14,17,18,27,43,49,54,63,64,69,72,73,77,88,97,99,114,119,123,132,143,148,153,154,157,158,162,163,174,179]},{"72":[11,36,91,106,111,116,121,166]},{"73":[6,16,56,91,96,116,136,146,161,176]},{"74":[6,21,26,31,36,46,81,121,156]},{"76":[0,1,2,12,22,24,34,53,57,77,78,84,97,102,113,114,117,119,123,128,134,137,139,144,152,162,172]},{"77":[16,31,56,76,91,111,116,141,146,151]},{"78":[41,66,101,111,131,136,151,176]},{"79":[6,36,46,51,56,81,141,156,161]},{"81":[0,23,28,29,32,37,38,43,52,64,69,92,98,108,112,117,122,129,148,152,158,173]},{"82":[6,36,66,96,116,126,131,136,166]},{"83":[36,46,56,61,66,71,76,86,101,111,141,156]},{"84":[16,46,61,66,71,86,116,121,136,146,156,166]},{"86":[1,4,7,17,18,19,22,23,27,28,34,39,47,52,54,69,77,83,87,89,94,122,133,134,142,144,152,153,158,164,172,177,178]},{"87":[6,56]},{"88":[6,11,16,51,76,141,146,151,166]},{"89":[16,71,96,101,106,156,161]},{"91":[0,4,12,34,39,44,49,52,53,57,58,63,68,69,73,77,88,99,113,119,143,147,149,162,164,172,173,174,178]},{"92":[6,16,21,41,76,116,126,141,166,176]},{"93":[51,56,66,91,101,121,161,176]},{"94":[26,46,76,86,121,126,136,146,166]},{"96":[24,38,42,43,53,54,64,82,87,88,92,93,99,102,108,109,119,124,127,129,147,158,164,167,169]},{"97":[6,11,31,51,66,71,76,101,146,151]},{"98":[6,61,81,91,101,116,121,136,141,161]},{"99":[6,46,66,111,121,136]},{"101":[8,13,24,33,38,44,57,58,63,64,67,82,83,84,88,89,92,97,98,99,107,113,133,138,143,149,152,158,162,169,172]},{"102":[31,91,136,146,156,161,176]},{"103":[21,31,46,56,71,106,126,141,146,156,171,176]},{"104":[41,51,71,76,81,96,146,156,166]},{"106":[3,8,13,17,23,32,33,34,37,39,53,58,62,67,74,79,92,98,103,107,119,123,127,143,144,148,149,172,174]},{"107":[16,26,36,46,91,96,136]},{"108":[6,56,76,81,106,141,161]},{"109":[36,96,106,111,121,136,141,166,171]},{"111":[3,13,18,19,23,24,29,32,34,39,47,54,72,79,84,98,102,109,112,123,127,137,152,154,157,158,164,169,172,174]},{"112":[16,31,46,51,61,66,91,96,101,121,156]},{"113":[16,41,46,81,121,141,146,156,166]},{"114":[11,31,76,111,146,151,156]},{"116":[1,2,3,14,24,39,48,73,77,79,99,103,139,144,159,167,172,174]},{"117":[6,16,36,96,106,146,151,156,166]},{"118":[11,26,51,61,76,126,156,161,176]},{"119":[6,56,91,111,146,151,166]}]'
rainbowmath_120_180_state2 = '[{"0":[11,76,116,166,171]},{"1":[6,21,41,51,76,101,136,146,151,156]},{"2":[11,46,51,81,126,131,136,161,171]},{"3":[11,31,96,126,136]},{"4":[16,21,26,46,91,131]},{"6":[1,24,28,29,32,39,44,49,62,84,88,94,103,108,113,122,123,128,132,133,143,148,152,154,158,167]},{"7":[6,41,46,51,76,146,161,166,176]},{"8":[6,51,71,86,106,116,131,146,151]},{"9":[36,81,151]},{"11":[1,3,14,19,22,28,42,54,57,67,74,78,79,98,102,104,124,134,138,147,157,163,168,169,172,173,174,178]},{"12":[16,46,71,96,106,116,156,166,176]},{"13":[6,11,51,61,76,81,131,141,156,161]},{"14":[11,21,26,86,96,156,161,171]},{"16":[4,22,23,27,52,83,88,89,92,97,102,103,104,112,119,138,142,159,162,164,169,173,178]},{"17":[11,31,46,71,76,91,116]},{"18":[11,31,46,76,86,101,106,111,116,136,151,161]},{"19":[16,21,56,71,131,151,156,161,171]},{"21":[1,2,22,24,33,34,39,49,57,64,69,74,83,102,104,107,108,122,127,134,137,139,142,144,147,152,154,163]},{"22":[76,81]},{"23":[26,66,71,101,106,116,131,146,151,161]},{"24":[6,31,81,86,116,141,151,171]},{"26":[2,12,13,27,39,53,54,62,63,79,84,87,97,108,109,123,134,142,147,149,159,167,178]},{"27":[26,36,41,51,76,86,141]},{"28":[21,26,36,46,66,81,86,116,121,131,151]},{"29":[26,56,61,71,101,111,116,151,156,161]},{"31":[3,13,14,23,34,42,43,48,67,73,83,84,87,88,93,107,117,118,122,128,132,137,148,153,177,178]},{"32":[31,36,41,51,71,76,86,106,166]},{"33":[11,16,21,36,41,76,91,106,121,126,141,156,166]},{"34":[71,76,81,106]},{"36":[1,13,28,58,64,77,82,98,113,117,124,132,133,142,143,152,153,159,162,168,169,173]},{"37":[6,36,41,51,56,96,151,166]},{"38":[16,26,41,61,91,96,101,106,111,131,156]},{"39":[16,31,71,81,136,141,146,176]},{"41":[13,14,37,43,47,57,63,64,79,82,84,87,103,104,123,124,134,153,157,158,169,174]},{"42":[21,101,106,121,146,151,176]},{"43":[21,41,61,66,76,81,86,91,116,126,151,176]},{"44":[11,36,46,81,86,101,121,141]},{"46":[2,3,12,14,22,23,33,39,54,63,72,79,84,92,102,104,107,127,128,134,143,158,159,163,168,172]},{"47":[6,21,51,76,101,116,121,136,151,156,171]},{"48":[21,81,131,151,166]},{"49":[6,11,36,41,56,96,106,151,156,161,166,176]},{"51":[0,9,17,23,34,37,44,49,59,63,68,78,84,89,97,102,104,108,112,113,118,124,127,133,134,144,148,159,163,179]},{"52":[31,36,56,81,126,131,136,141,171,176]},{"53":[6,11,26,46,51,56,86,96,111,121,126,166,176]},{"54":[46,71,91,101,116,131,136,141,146,156]},{"56":[0,1,3,19,27,32,38,48,52,63,74,78,83,84,87,93,94,99,102,103,107,108,113,114,132,142,143,154]},{"57":[11,16,21,26,31,41,51,86,111,121,131,151,161]},{"58":[16,21,46,51,76,86,101,151,171]},{"59":[11,36,71,106,161,176]},{"61":[8,13,24,29,39,42,48,53,57,63,69,79,88,89,92,97,102,108,109,117,127,129,144,157,158,178]},{"62":[6,86,91,96,106,126,171]},{"63":[6,41,56,66,71,76,96,136,146]},{"64":[6,16,36,56,71,91,126,151,166]},{"66":[1,2,7,12,17,27,28,29,32,37,38,43,49,57,62,63,67,68,69,102,108,112,122,127,128,129,134,138,148,149,154,163,168,172,178]},{"67":[16,26,36,66,86,116,136,156,161]},{"68":[11,16,21,51,66,71,106,151,161,166,171]},{"69":[21,26,41,66,76,101,126,136,161]},{"71":[8,9,13,28,29,34,37,42,44,58,78,79,87,93,98,102,108,113,122,128,137,142,164,167,168,172]},{"72":[41,71,96,126,131,141,161,176]},{"73":[11,26,51,61,76,101,111,151,156]},{"74":[71,96,116,126]},{"76":[3,4,9,14,18,27,29,39,52,54,59,62,64,68,69,74,79,89,92,94,98,107,108,124,127,129,138,143,147,148,154,158,163,177]},{"77":[11,21,96,106,161,171]},{"78":[46,56,71,81,91,96,121,146,156,166]},{"79":[41,66,86,101,116,131,136,146,171,176]},{"81":[2,4,14,18,22,33,49,53,57,62,67,72,77,79,82,88,89,103,104,119,124,137,139,147,162,163,164,172,174,178]},{"82":[11,26,31,46,51,76,81,91,106,171]},{"83":[6,11,16,51,106,136,146]},{"84":[6,56,91,101,106,131,171,176]},{"86":[8,9,13,14,24,32,37,49,58,59,63,64,68,73,78,84,88,98,99,103,112,113,114,128,132,143,149,154,157,163]},{"87":[41,46,96,111,121,126,156,161]},{"88":[26,41,61,91,101,111,121,156,161]},{"89":[6,11,26,61,91,126,176]},{"91":[1,8,13,17,22,43,54,59,67,79,84,87,92,98,108,117,127,129,137,138,139,142,144,153,159,163,167,177]},{"92":[26,36,46,81,91,101,146]},{"93":[16,31,41,46,61,81,106,116,126,131,136,146,166]},{"94":[11,16,21,51,56,61,71,96,106,131,156,161]},{"96":[0,1,2,12,18,22,27,37,52,62,67,74,78,83,94,103,107,114,117,118,133,138,139,142,143,144,148,154,159,163,174,178]},{"97":[26,81,91,161,176]},{"98":[11,16,41,46,106,146,171]},{"99":[11,21,26,31,51,56,71,86,91,141,151,171]},{"101":[1,14,17,28,29,34,42,47,69,72,74,78,93,102,103,109,114,117,118,122,123,137,139,142,147,153,154,168,174,177,179]},{"102":[11,16,41,81,101,121,131,141,151,166]},{"103":[26,61,86,96,101,131,136,151,166]},{"104":[6,16,26,36,56,66,106,136,151,171,176]},{"106":[0,1,4,7,12,18,22,38,57,63,68,87,89,93,97,99,108,109,122,157,159,177]},{"107":[11,76,111,116,126,156,176]},{"108":[31,86,101,111,121,126,146,166,176]},{"109":[41,46,76,116,131,151]},{"111":[2,8,9,17,42,43,49,57,64,68,88,89,92,99,113,117,122,124,133,134,138,139,144,147,153,159,162,167,173,179]},{"112":[6,11,26,36,56,71,76,81,106,136,161]},{"113":[6,11,26,56,61,71,76,111,116,171]},{"114":[21,51,81,91,96,106,126,131,136,161,176]},{"116":[7,17,18,22,23,28,29,33,37,42,47,53,62,63,82,83,84,98,104,107,109,112,113,123,128,129,137,147,148,157,158,168,173]},{"117":[11,26,116,121]},{"118":[36,41,46,71,81,91,101,111,121,171]},{"119":[16,51,71,76,81,121,131,141,176]}]'

rainbowmath_120_180_rows = 120
rainbowmath_120_180_cols = 180

rainbowmath_120_180_finegrained_gold = [
    [0, 1280, 1280, 0],
    [1, 1070, 1066, 2224],
    [2, 1651, 1662, 1434],
    [3, 1669, 1642, 924]
]

# ----------------
# Random map, 100 x 120

random_100_120_state1 = '[{"0":[0,17,89,96,103,104,116]},{"1":[4,36,37,38,70,74,101,108]},{"2":[10,11,29,36,42,74,90,115,118]},{"3":[1,13,23,34,43,48,54,55,68,69,77,83]},{"4":[8,15,28,50,60,67,100]},{"5":[15,16,50,53,63,65,75,85,112,118]},{"6":[0,1,7,9,29,31,49,53,71,93,102,104]},{"7":[3,64,94,102,119]},{"8":[26,31,74,80,89,91,112,115]},{"9":[1,12,26,29,32,36,54,62,83,100,103]},{"10":[46,57,74,103]},{"11":[16,28,51]},{"12":[10,13,23,33,65,79,119]},{"13":[28,37,42,60,74,105]},{"14":[19,24,41,63,93]},{"15":[9,36,56,61,66,68,80,87,105,109,111]},{"16":[5,12,21,26,37,39,55,62,82,88,96,98,112]},{"17":[13,37,43,44,51,75,80,94,107,112,114]},{"18":[2,21,30,36,44,46,63,70,71,73,81,84,95,109,111,119]},{"19":[13,41,58,63,65,66,73,82,83,97,103,108]},{"20":[16,25,41,63,79,116]},{"21":[9,38,39,59,64,70,84]},{"22":[3,5,32,33,65,106]},{"23":[33,53,59,65,69,74,90,114]},{"24":[2,48,58,61,64,66,90,91]},{"25":[13,16,61,69,74,81,82,101,105,109]},{"26":[20,28,46,47,53,68,73,84,85,93,94]},{"27":[26,42,65,66,70,94,99,103,111]},{"28":[6,12,71,81,97,103,113]},{"29":[32,41,44,81,86,118]},{"30":[27,35,40,48,98,100,117]},{"31":[6,13,22,40,61,82,83,90,106]},{"32":[37,43,50,92,105,112,115]},{"33":[26,45,47,62,70,82,117]},{"34":[3,6,17,19,27,36,58,62,85,92,106,112]},{"35":[2,3,4,15,39,96]},{"36":[2,5,9,14,31,32,36,73]},{"37":[19,25,37,42,59,69,70,74,91]},{"38":[4,25,55,57,65,68,88,117]},{"39":[5,20,42,83,114]},{"40":[17,46,64,87,91,105]},{"41":[8,15,23,36,42,49,53,81,86,91,93,102,110,113]},{"42":[2,4,31,38,52,66,83,98,116]},{"43":[19,30,36,39,40,62,70,85,92,98,104]},{"44":[9,21,58,71,89,95,96,106]},{"45":[9,12,19,51,62,69,79]},{"46":[1,22,33,37,57,68,70,74,90]},{"47":[8,33,44,45,48,69,83,105,114]},{"48":[4,9,42,44,46,57,68,92,102]},{"49":[11,25,30,59,62,78,98]},{"50":[8,22,33,57,91,95,96]},{"51":[0,6,11,16,27,33,35,64,83,96]},{"52":[5,39,55,66,83,85,87]},{"53":[12,23,26,35,37,51,66,85,87,98,115]},{"54":[15,28,63,79,84]},{"55":[7,77,84,110,119]},{"56":[19,37,41,59,61,62,73,92,110]},{"57":[10,41,62,86]},{"58":[1,49,108,109]},{"59":[3,5,14,18,40,53,69,77,86,90]},{"60":[18,26,37,43,87,90,98]},{"61":[2,12,13,21,29,84,85,99,105,115]},{"62":[4,30,39,61,78,104]},{"63":[2,7,8,28,41,44,49,54,68,84,91,102]},{"64":[12,14,25,29,30,36,38,54,67,93,104]},{"65":[35,40,54,59,66,67,107,110,117]},{"66":[4,7,11,55,90,97,105,114]},{"67":[27,46,51,56,58,70,94,100]},{"68":[32,45,46,48,62,84,86,87,97,110]},{"69":[17,22,94,106]},{"70":[13,26,67,79,110,119]},{"71":[8,20,21,36,64,75,83,98,102,110,111]},{"72":[11,23,38,40,81]},{"73":[28,33,64,65,80,92,93]},{"74":[23,42,53,58,90,97,106]},{"75":[1,11,20,30,101,104,107,114]},{"76":[6,7,28,35,47,67,73,94]},{"77":[62,86,88,94,96,99,102]},{"78":[20,40,64,76,79,80,82,92,109]},{"79":[21,51]},{"80":[63,94,103,107,114]},{"81":[36,48,58,84,86,110]},{"82":[47,48,56,76,80]},{"83":[5,17,26,32,45,65,68,71,75,80]},{"84":[42,87,119]},{"85":[6,14,34,37,81,112]},{"86":[4,7,31,51,70,72,86,100]},{"87":[1,8,28,46,70,78,105,106]},{"88":[27,36,56,88,101]},{"89":[8,15,23,29,42,55,101]},{"90":[19,34,51,66,74,80,96,105]},{"91":[17,48,76,88,102,103,110]},{"92":[4,6,11,16,64,109,119]},{"93":[12,20,22,31,34,39,79,82,110]},{"94":[23,27,43,49,70,83,100,106]},{"95":[15,23,36]},{"96":[0,4,74,86,100]},{"97":[5,22,34,38,60,85,111,114,116]},{"98":[88,97]},{"99":[25,30,35,39,86,92,103,105,115,116]}]'
random_100_120_state2 = '[{"0":[3,5,8,20,24,39,43,45,48,65,67,98]},{"1":[13,14,40,48,53,60,80,81,85]},{"2":[6,44,45,49,70,79,99,107,111]},{"3":[3,7,21,26,44,49,58,66,75,90,102,113]},{"4":[0,11,21,49,63,78,96]},{"5":[44,69,70]},{"6":[46,48,51,68,69,89,108]},{"7":[5,11,20,36,45,65,88,92,110,115]},{"8":[10,13,25,33,37,38,90,116]},{"9":[11,16,28,40,41,42,47,69,72,79,85,106,113]},{"10":[7,30,60,70,95]},{"11":[6,29,39,48,76,107,117]},{"12":[0,7,9,12,21,36,68,76,100]},{"13":[21,24,26,38,51,69,107,114,119]},{"14":[10,12,33,55,95,96,115]},{"15":[46,52,69,72,89]},{"16":[2,17,30,33,38,49,102,108]},{"17":[2,15,18,65,100]},{"18":[27,35,59]},{"19":[5,11,21,24,101]},{"20":[3,7,15,21,53,62,80,82,83,85,109]},{"21":[3,21,45,51,67,72,76,83,88]},{"22":[30,45,76,78,79]},{"23":[12,13,20,50,61,89,104,119]},{"24":[25,60,65,70,100,103,105]},{"25":[1,65,102,110]},{"26":[3,15,27,75,107,114]},{"27":[11,43]},{"28":[1,8,20,32,40,47,48,56,107,109,112]},{"29":[13,14,18,26,35,36,58,93,96,117]},{"30":[7,13,29,31,55,73,79,92,102,110,113,116,119]},{"31":[20,79,119]},{"32":[19,46,52,56,80,89,100]},{"33":[60,63,65,76,101,102,104,108]},{"34":[0,4,5,11,15,18,28,43,46,87,97]},{"35":[11,37,53,55,60,68,77,84,108]},{"36":[3,13,16,35,48,58,60,62,68,77,84,86,88,90,93,97,112,119]},{"37":[20,30,94,112]},{"38":[39,41,71,93,102]},{"39":[7,9,15,17,19,59,61,72,79,85,92]},{"40":[0,14,29,39,47,56,71,85,103,109]},{"41":[0,6,21,26,30,56,62,71,98,107]},{"42":[25,35,47,86,89,96,97]},{"43":[0,22,35,60,93,103]},{"44":[10,23,33,37,47,53,57,67,68,72,99]},{"45":[23,52,67,75,99,104,108,110]},{"46":[16,40,43,60,81,83,98,102,105,109]},{"47":[9,59,87,92]},{"48":[0,3,10,24,60,72,82,87,88]},{"49":[36,72,80,81,84,91,101,103]},{"50":[2,20,30,45,46,59,63,79,81,84,89,108]},{"51":[9,14,28,51,57,62,77,81,88,89,98,99,118]},{"52":[9,19,42,69,96,102]},{"53":[1,56,63,65,71,92,102,109]},{"54":[10,17,18,35,53,56,80,91,95,101,116]},{"55":[12,19,42,46,53,54,93]},{"56":[8,12,34,43,53,77,90,105,109]},{"57":[12,26,69,75,76,80,99,101,106]},{"58":[2,34,36,39,86,107]},{"59":[2,23,28,44,85,116]},{"60":[25,28,35,55,73,103,105]},{"61":[15,24,30,48,57,87,95,97,111]},{"62":[27,67,77,88,90,101,112]},{"63":[9,33,48,57,64,67,69,119]},{"64":[6,18,47,74,75,97,112]},{"65":[3,5,64,74,86,97,111,115]},{"66":[1,32,40,47,54,64,67,69,72,104,107]},{"67":[18,19,21,25,29]},{"68":[3,21,22,30,40,54,66]},{"69":[0,19,35,42,54,67,77,81,101]},{"70":[12,46,50,106]},{"71":[5,14,28,57,62,71,74,78,84,90]},{"72":[2,13,17,47,63,84,97,106,114]},{"73":[3,6,39,73,83,84,99,116,117]},{"74":[8,47,65,67,82,87,92,108,110]},{"75":[25,32,47,48,82,90,115]},{"76":[9,21,38,43,53,75,83,91,92,95]},{"77":[3,16,54,66,69,79,119]},{"78":[37,65,84,102,106,118]},{"79":[1,31,44,78,89,98]},{"80":[8,10,13,18,33,79,81,93,115]},{"81":[6,13,19,32,42,46,100,117]},{"82":[24,46]},{"83":[22,27,28,29,38,46,81,82,99,106,118]},{"84":[7,38,48,74,86,108,110]},{"85":[46,48,50,56,96,101]},{"86":[1,16,21,47,84,88,91]},{"87":[33,39,44,60,67,95,107,108,111]},{"88":[53,108]},{"89":[5,13,18,21,52,66,92]},{"90":[0,9,42,59,63,69,89,92,94]},{"91":[36,37,39,51,56,72,90,117,119]},{"92":[9,28,101,104,110,117]},{"93":[7,17,29,35,36,48,75,114,119]},{"94":[21,52,53,68,82,116]},{"95":[18,48,53,64,67,93,103]},{"96":[8,9,11,14,41,49,65,89,109]},{"97":[13,30,37,39,47,89,98]},{"98":[7,10,49,50,77,89,105,109]},{"99":[31,46]}]'

random_100_120_rows = 100
random_100_120_cols = 120

random_100_120_final = [1052, 34, 14, 0]

random_100_120_finegrained_gold = [
    [0, 1280, 1280, 0],
    [1, 1070, 1066, 2224],
    [2, 1651, 1662, 1434],
    [3, 1669, 1642, 924]
]
