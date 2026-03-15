from scripts._util_general.file_util import read_file, write_file
from pathlib import Path


def generate(install_path:str, *, output_path:str="./", lang):
    global char_classes

    char_classes = {char_class["code"]: {"traits":char_class["traits"], "gear": char_class["gear"]} for char_class in read_file(install_path + "/assets/survival/config/characterclasses.json", decode_json=True)}

    for char_class_dict in char_classes.values():
        char_class_dict["gear"] = [char_class_dict["gear"][i]["code"] for i in range(len(char_class_dict["gear"]))]

    write_file(output_path+"generated/char_classes.json", char_classes, encode_json=True)

### destinction_fun expects a function to specify what kinda of items are wanted. It should be able to receive 1 string parameter e.g.:
###   `char_class_gear_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))` to narrow it down to just clothing items.
def char_class_gear_by_type(destinction_fun):
    out={}
    for char_class in char_classes:
        for item in char_classes[char_class]["gear"]:
            if destinction_fun(item):
                if item not in out:
                    out[item]=[]
                out[item].append("class-equipment-"+char_class)
    return out