# This was a standalone tool that I initially used to generate the midpointlist.csv file.
# It can be optimized.
def get_midpoints(in_path) -> str:
    import codecs
    from PIL import Image

    definition = codecs.open(in_path + "/definition.csv", encoding="latin_1").read()
    lines = definition.split("\n")

    provinces_dict = {}

    provinces_map = Image.open(in_path + "/provinces.bmp", 'r')
    map_width = provinces_map.size[0]
    provinces_map = list(provinces_map.getdata())
    # width 5632 for basegame map

    for line in lines:
        line = line.split(';')
        if line[0] != "province" and len(line[0]) > 0:
            provinces_dict[tuple([int(line[1]), int(line[2]), int(line[3])])] = line[0]

    mod_id = in_path.split('/')[-2]
    out_file_path = f"mod_data/{mod_id}midpointlist.csv"
    out_file = open(out_file_path, 'w')

    province_pixel_dict = {}

    for p in range(len(provinces_map)):
        coords = (p % map_width, int(p / map_width))
        try:
            if provinces_dict[provinces_map[p]] in province_pixel_dict.keys():
                province_pixel_dict[provinces_dict[provinces_map[p]]].append(coords)
            else:
                province_pixel_dict[provinces_dict[provinces_map[p]]] = [coords]
        except:  # Province doesn't exist in the map
            pass

    out_str = ""
    for key in province_pixel_dict.keys():
        x_total = 0
        y_total = 0
        for coord_set in province_pixel_dict[key]:
            x_total += coord_set[0]
            y_total += coord_set[1]
        x_total /= len(province_pixel_dict[key])
        y_total /= len(province_pixel_dict[key])
        out_str += f"{key},{x_total},{y_total}\n"

    out_file.write(out_str)

    out_file.close()
    return out_file_path
