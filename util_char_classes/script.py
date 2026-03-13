from pathlib import Path
import json
from _util_general.json_util import repair
from _util_general.mediawiki_templates import tunit


def setup(install_path:str, *, output_path:str="./", lang):
    global char_classes
    Path(output_path+"/generated").mkdir(parents=True, exist_ok=True)

    with open(install_path+"/assets/survival/config/characterclasses.json", "r") as f:
        char_classes = {char_class["code"]: {"traits":char_class["traits"], "gear": char_class["gear"]} for char_class in json.loads(repair(f.read()))}

    for char_class_dict in char_classes.values():
        char_class_dict["gear"] = [char_class_dict["gear"][i]["code"] for i in range(len(char_class_dict["gear"]))]

    with open(output_path+"generated/char_classes.json", "x") as f:
        f.write(json.dumps(char_classes, indent=4))


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
    #return {item: [[soil, panning_items[soil][item]] for item in panning_items[soil]] for soil in panning_items}

    return json.loads(json.dumps(out))