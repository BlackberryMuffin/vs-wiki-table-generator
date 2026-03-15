import json

from scripts._util_general.file_util import read_file, write_file
from os import listdir
from scripts._util_general.mediawiki_templates import tunit
from scripts.util_0lang.script import get_dict

def generate(install_path:str, *, output_path:str="./", lang):
    global traders_json, trades, traders_lang_dict

    path = install_path+"/assets/survival/config/tradelists/"

    trader_files = listdir(path)

    traders_json={}
    for trader_file in trader_files:
        traders_json[trader_file[:-5]] = read_file(path+trader_file, decode_json=True)

    write_file(output_path+"/generated/traders.json", traders_json, encode_json=True)

    trades = {}
    directions = ["selling", "buying"]
    for trader in traders_json:
        for direction in directions:
            for listings in traders_json[trader][direction]["list"]:
                if not listings["code"] in trades:
                    trades[listings["code"]] = {d:[] for d in directions}
                #trades[listings["code"]][direction].append(very_specific_function(trader, listings))
                trades[listings["code"]][direction].append((trader, listings))
    lang_dict = get_dict(lang)
    traders_lang_dict = {"trader-"+(trader_id[23:][:-5]): (lang_dict[trader_id][:-7]) for trader_id in lang_dict if trader_id.startswith("item-creature-trader") and trader_id.endswith("-cold")} |\
                        {"villager-"+(villager_id.split("-")[-1]): "Village "+(lang_dict[villager_id].lower()) for villager_id in lang_dict if villager_id.startswith("item-creature-villager") and not villager_id.endswith("generic")}
    write_file(output_path+"/generated/trader_lang.json", traders_lang_dict, encode_json=True)


def translate_trader(install_path:str, trader:str, *, lang:str="en", addTunit:bool=False, villagerCounter:list=None):
    name = traders_lang_dict[trader]
    villager = trader.startswith("villager-")
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



















