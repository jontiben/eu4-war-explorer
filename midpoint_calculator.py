# This was a standalone tool that I initially used to generate the midpointlist.csv file.
# It can be optimized.
def get_midpoints(in_path) -> str:
    import codecs
    from PIL import Image

    definition = codecs.open(in_path + "/definition.csv", encoding="latin_1").read()
    lines = definition.split("\n")

    PROVINCES_DICT = {}

    PROVINCES_MAP = Image.open(in_path + "/provinces.bmp", 'r')
    MAP_WIDTH = PROVINCES_MAP.size[0]
    PROVINCES_MAP = list(PROVINCES_MAP.getdata())
    # width 5632 for basegame map

    for line in lines:
        line = line.split(';')
        if line[0] != "province" and len(line[0]) > 0:
            PROVINCES_DICT[tuple([int(line[1]), int(line[2]), int(line[3])])] = line[0]

    mod_id = in_path.split('/')[-2]
    out_file_path = f"mod_data/{mod_id}midpointlist.csv"
    out_file = open(out_file_path, 'w')

    PROVINCE_PIXEL_DICT = {}

    for p in range(len(PROVINCES_MAP)):
        coords = (p % MAP_WIDTH, int(p / MAP_WIDTH))
        try:
            if PROVINCES_DICT[PROVINCES_MAP[p]] in PROVINCE_PIXEL_DICT.keys():
                PROVINCE_PIXEL_DICT[PROVINCES_DICT[PROVINCES_MAP[p]]].append(coords)
            else:
                PROVINCE_PIXEL_DICT[PROVINCES_DICT[PROVINCES_MAP[p]]] = [coords]
        except:  # Province doesn't exist in the map
            pass

    out_str = ""
    for key in PROVINCE_PIXEL_DICT.keys():
        x_total = 0
        y_total = 0
        for coord_set in PROVINCE_PIXEL_DICT[key]:
            x_total += coord_set[0]
            y_total += coord_set[1]
        x_total /= len(PROVINCE_PIXEL_DICT[key])
        y_total /= len(PROVINCE_PIXEL_DICT[key])
        out_str += f"{key},{x_total},{y_total}\n"

    out_file.write(out_str)

    out_file.close()
    return out_file_path
