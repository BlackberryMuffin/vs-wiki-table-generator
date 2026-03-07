def generate_tables(install_path:str, *, output_path:str="./"):
    from os import listdir, mkdir
    import json
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

def translate_trader(install_path:str, trader:str, *, lang:str="en"):
    import json

    with open(f"{install_path}/assets/game/lang/{lang}.json", "r") as f:
        lang_dict=json.load(f)

    return lang_dict[f"item-creature-{trader.replace("-","-*-")}-cold"][:-7]  if trader.startswith("trader-") else lang_dict[trader.replace("villager", "nametag")]

