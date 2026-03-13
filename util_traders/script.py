from os import listdir, mkdir
import json
from _util_general.mediawiki_templates import tunit
from _util_general.lang_dicts import get_dict

def setup(install_path:str, *, output_path:str="./", lang):
    global traders_json
    global trades

    path = install_path+"/assets/survival/config/tradelists/"

    trader_files = listdir(path)

    traders_json={}
    for trader_file in trader_files:
        with open(path+trader_file, "r") as f:
            traders_json[trader_file[:-5]]=json.load(f)

    mkdir(output_path+"/generated")
    with open(output_path+"/generated/traders.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(traders_json, indent=4))

    trades = {}
    directions = ["selling", "buying"]
    for trader in traders_json:
        for direction in directions:
            for listings in traders_json[trader][direction]["list"]:
                if not listings["code"] in trades:
                    trades[listings["code"]] = {d:[] for d in directions}
                #trades[listings["code"]][direction].append(very_specific_function(trader, listings))
                trades[listings["code"]][direction].append((trader, listings))


def translate_trader(install_path:str, trader:str, *, lang:str="en", addTunit:bool=False, villagerCounter:list=None):
    langs_dict=get_dict(install_path, lang)

    name = ""
    villager = False
    if trader.startswith("trader-"):
        name = langs_dict[f"item-creature-{trader.replace("-","-*-")}-cold"][:-7]
    else:
        name = langs_dict[trader.replace("villager", "nametag")]
        villager = True
    if addTunit:
        name = tunit(trader,name)
    if villager and type(villagerCounter) is list:
        name += "<sup>_-XYZ-_</sup>"
        villagerCounter[0]+=1

    return name


def get_trader_ids():
    return [trader for trader in traders_json]


### destinction_fun expects a function to specify what kinda of items are wanted. It should be able to receive 1 string parameter e.g.:
###   `trades_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))` to narrow it down to just clothing items.
def trades_by_type(destinction_fun):
    return {item:trades[item] for item in trades if destinction_fun(item)}



















