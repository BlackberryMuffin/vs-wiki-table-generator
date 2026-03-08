from os import listdir, mkdir
import json

langs_dict={}


def generate_tables(install_path:str, *, output_path:str="./"):
    global traders_json

    path = install_path+"/assets/survival/config/tradelists/"

    trader_files = listdir(path)

    traders_json={}
    for trader_file in trader_files:
        with open(path+trader_file, "r") as f:
            traders_json[trader_file[:-5]]=json.load(f)

    mkdir(output_path+"/generated")
    with open(output_path+"/generated/traders.json", "x") as f:
        f.write(json.dumps(traders_json, indent=4))




def translate_trader(install_path:str, trader:str, *, lang:str="en", addTunit:bool=False):
    if lang not in langs_dict:
        with open(f"{install_path}/assets/game/lang/{lang}.json", "r") as f:
            langs_dict[lang]=json.load(f)

    name = ""
    villager = False
    if trader.startswith("trader-"):
        name = langs_dict[lang][f"item-creature-{trader.replace("-","-*-")}-cold"][:-7]
    else:
        name = langs_dict[lang][trader.replace("villager", "nametag")]
        villager = True
    if addTunit:
        name = f"{{{{Tunit|{trader}|{name}}}}}"

    return name

