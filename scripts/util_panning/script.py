from scripts._util_general.file_util import read_file, write_file, write_file_safe
from pathlib import Path
import json
from scripts._util_general.json_util import repair
from scripts._util_general.mediawiki_templates import tunit


def generate(install_path:str, *, output_path:str="./", lang):
    global panning_items

    panning_items = read_file(install_path+"/assets/survival/blocktypes/wood/pan.json", decode_json=True)["attributes"]["panningDrops"]

    panning_items[tunit("table-content-panning-bonysoil", "Obtainable from panning bony soil")]=panning_items.pop('@(bonysoil|bonysoil-..*)')
    panning_items[tunit("table-content-panning-other", "Obtainable from panning gravel or sand")]=panning_items.pop('@(sand|gravel|sandwavy)-..*')
    total_chances={}
    for soil in panning_items:
        total_chances[soil]=0
        tmp={}
        for item in panning_items[soil]:
            if item["chance"]["var"] != 0 or item["code"] in tmp:
                raise Exception("WHAAAAAAAAAAA; THEY CHNAGED THE JSONS")
            tmp[item["code"]]=item["chance"]["avg"]
            total_chances[soil]+=tmp[item["code"]]
        panning_items[soil]=tmp


    write_file(output_path + "generated/total_chances.json", total_chances, encode_json=True)
    write_file(output_path+"generated/pan.json", panning_items, encode_json=True)

### destinction_fun expects a function to specify what kinda of items are wanted. It should be able to receive 1 string parameter e.g.:
###   `pannable_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))` to narrow it down to just clothing items.
def pannable_by_type(destinction_fun):
    out={}
    for soil in panning_items:
        for item in panning_items[soil]:
            if destinction_fun(item):
                if item not in out:
                    out[item]=[]
                out[item].append([soil, panning_items[soil][item]])
    #return {item: [[soil, panning_items[soil][item]] for item in panning_items[soil]] for soil in panning_items}

    return json.loads(json.dumps(out))