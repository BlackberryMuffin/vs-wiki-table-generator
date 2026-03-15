from pathlib import Path
import json
from _util_general.json_util import repair
from _util_general.mediawiki_templates import tunit


def generate(install_path:str, *, output_path:str="./", lang):
    global panning_items
    Path(output_path+"/generated").mkdir(parents=True, exist_ok=True)

    with open(install_path+"/assets/survival/blocktypes/wood/pan.json", "r") as f:
        panning_items=json.loads(repair(f.read()))["attributes"]["panningDrops"]

    panning_items[tunit("table-content-panning-bonysoil", "Obtainable from panning bony soil")]=panning_items['@(bonysoil|bonysoil-..*)']
    del panning_items['@(bonysoil|bonysoil-..*)']
    panning_items[tunit("table-content-panning-other", "Obtainable from panning gravel or sand")]=panning_items['@(sand|gravel|sandwavy)-..*']
    del panning_items['@(sand|gravel|sandwavy)-..*']
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


    with open(output_path + "generated/total_chances.json", "x") as f:
        f.write(json.dumps(total_chances, indent=4))
    with open(output_path+"generated/pan.json", "x") as f:
        f.write(json.dumps(panning_items, indent=4))


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