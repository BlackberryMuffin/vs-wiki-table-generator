import json
import util_traders.script as trader_util
from pathlib import Path
from _util_general.mediawiki_templates import tunit, hovertip
from _util_general.lang_dicts import get_dict
from _util_general.json_util import repair as repair_json
from os import scandir
import re

debug = True

"""
    Seperately from "generated/table.txt", the script will produce "generated/translation_help.txt".
    If its content has not yet been placed in the wiki page of the table, it is to be placed below the <languages/> tag at the top of the page.
    Without it, this table will not translate properly.
        It can technically be anywhere, but this placement reduces the risk of it being deleted by accident.
"""

special_tunit_entries=[
    ("item-gear-rusty", "rusty gears"),
]

special_names=["nadiya"]
interpret_as={"butterflypin":"emblem"}
def generate(install_path:str, *, output_path:str="./", lang:str="en"):
    Path(output_path+"/generated/tables").mkdir(parents=True, exist_ok=True)

    en_lang_dict=get_dict(install_path, lang="en")
    lang_dict=get_dict(install_path, lang=lang)
    gen_clothing_attributes(install_path, output_path, gen_cleaned_jsons=True)

    items={}
    warmth={}
    rain_prot={}
    eye_prot={}
    descriptions={}
    sold_by={}
    bought_by={}
    craftable={}


    # Fills `items` (used for item-id + item name) and `descriptions` (used for item lore text) from the games translation files
    for key in en_lang_dict:
        if key.startswith(("item-clothes-")):
            items[key[5:]] = (lang_dict if key in lang_dict else en_lang_dict)[key]

        if key.startswith(("itemdesc-clothes-")):
            descriptions[key[9:]] = (lang_dict if key in lang_dict else en_lang_dict)[key]


    #TODO: warmth
    for item in items:
        attributes = get_attributes(item)
        if attributes is None:
            continue
        if "warmth" in attributes and attributes["warmth"]:
            warmth[item] = f"{attributes["warmth"]}°C"
        if "rainProtectionPerc" in attributes and attributes["rainProtectionPerc"]:
            tmp = attributes["rainProtectionPerc"]*100
            rain_prot[item] = f"{int(tmp) if tmp==int(tmp) else tmp}%"
        if "eyeprotective" in attributes and attributes["eyeprotective"]:
            eye_prot[item] = "✅" ### <-- In case your font doesn't support it, that's a green checkmark :D

    test_var_out = list(test_var)
    test_var_out.sort()
    if debug:
        with open(output_path+"generated/attributes", "x", encoding="utf-8") as f:
            f.write("\n".join(test_var_out))


    #TODO: rain prot

    #TODO: eye:prot


    # A lambda function which generates a string like "{{Hovertip|{{Tunit|trader-treasurehunter|Treasure hunter trader}}|1.5 - 2.5 {{Tunit|item-gear-rusty|rusty gears}}}}" from trade information
    contains_villagers=[0]
    very_specific_function = lambda trader, trade: hovertip(trader_util.translate_trader(install_path, trader, addTunit=True, villagerCounter=contains_villagers), f"{trade["price"]["avg"]-trade["price"]["var"]} - {trade["price"]["avg"]+trade["price"]["var"]} {{{{Tunit|item-gear-rusty|rusty gears}}}}")
    # Fetches all clothing trades from trader_util
    trades = trader_util.trades_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))
    # The previously fetched trade data is now modified using very_specific_function and then added `sold_by` and `bought_by` which hold readable trade information
    for clothing in trades:
        sold_by[clothing] = [very_specific_function(*trade) for trade in trades[clothing]["selling"]]
        bought_by[clothing] = [very_specific_function(*trade) for trade in trades[clothing]["buying"]]

    #TODO: craftable



    out=""+\
        "{|<!--\n"+\
        "This tables layout was generated automatically via https://github.com/BlackberryMuffin/vs-wiki-table-generator. If you want to modify this tables layout, consider changing the code directly instead the table's source text!\n"+\
        '-->class="wikitable sortable mw-collapsible" style="text-align:center;"\n'+\
        "|+<translate>Clothing</translate>||-;"+\
        "\n"+\
        "!<translate>Item icon</translate><ref><code>assets/game/lang/en.json</code></ref>"+\
        "!!<translate>Item name</translate><ref><code>assets/game/lang/</code></ref>"+\
        ('!!data-sort-type="number"|<translate>Warmth</translate><ref><code>assets/survival/itemtypes/wearable/seraph/</code></ref>' if len(warmth) != 0 else "")+\
        ('!!data-sort-type="number"|<translate>Rain prot.</translate><ref><code>assets/survival/itemtypes/wearable/seraph/</code></ref>' if len(rain_prot) != 0 else "")+\
        ("!!<translate>Eye prot.</translate><ref><code>assets/survival/itemtypes/wearable/seraph/</code></ref>" if len(eye_prot) != 0 else "")+\
        ("!!<translate>Item description</translate><ref><code>assets/game/lang/</code></ref>" if len(descriptions) != 0 else "")+\
        ("!!<translate>Bought from</translate><ref><code>assets/survival/config/tradelists/</code></ref>" if len(sold_by) != 0 else "")+\
        ("!!<translate>Sold to</translate><ref><code>assets/survival/config/tradelists/</code></ref>" if len(bought_by) != 0 else "")+\
        ("!!<translate>Craftable</translate><ref><code>assets/survival/recipes/grid/clothes/</code></ref>" if len(craftable) != 0 else "")+\
        "\n"+\
        "|-\n"

    for item in items:

        out+=""+\
            f"|[[File:{item}.png|64px]]"+\
            f"||<translate>{items[item]}</translate>"+\
            (f"||{f"<translate>{warmth[item]}</translate>" if item in warmth else ""}" if len(warmth) != 0 else "")+\
            (f"||{f"<translate>{rain_prot[item]}</translate>" if item in rain_prot else ""}" if len(rain_prot) != 0 else "")+\
            (f"||{f"<translate>{eye_prot[item]}</translate>" if item in eye_prot else ""}" if len(eye_prot) != 0 else "")+\
            (f"||{f"<translate>{descriptions[item]}</translate>" if item in descriptions else ""}" if len(descriptions) != 0 else "")+\
            (f"||{f"{",<br>".join(sold_by[item])}" if item in sold_by else ""}" if len(sold_by) != 0 else "")+\
            (f"||{f"{",<br>".join(bought_by[item])}" if item in bought_by else ""}" if len(bought_by) != 0 else "")+\
            (f"||{f"<translate>{craftable[item]}</translate>" if item in craftable else ""}" if len(craftable) != 0 else "")+\
            "\n|-\n"
    out+=""+\
        "|}"+\
        ("<sup>1</sup> <translate>Villagers, while similar to {{ll|Trading|traders}} are seperate. At the risk of spoiling the game's story, see {{ll|Villager}} and/or {{ll|Village}} if you want to learn more.</translate>" if contains_villagers[0] else "")


    with open(output_path+"/generated/tables/all.txt", "x", encoding="utf-8") as f:
        f.write(out)

    trans_help=["<!--This is here for easier translation of the table using Tunit. Do not touch this if you don't know what you're doing!-->", "{{Hovertip||"]
    tunit_entries = special_tunit_entries + [(trader, trader_util.translate_trader(install_path, trader, lang=lang)) for trader in trader_util.get_trader_ids()]
    trans_help += [f"<translate><!--T:{entry[0]}--> {entry[1]}</translate>" for entry in tunit_entries] + ["}}", trans_help[0]]
    with open(output_path+"/generated/translation_help.txt", "x", encoding="utf-8") as f:
        f.write("\n".join(trans_help))




def gen_clothing_attributes(install_path:str, output_path:str, *, gen_cleaned_jsons:bool=False):
    global clothing_attributes
    if "clothing_attributes" in globals():
        return
    if gen_cleaned_jsons:
        Path(output_path + "/generated/cleaned_jsons").mkdir(parents=True, exist_ok=True)

    clothing_attributes={}

    sub_dirs=[(install_path+"/assets/survival/itemtypes/wearable/seraph/", "")]
    i=0
    while i < len(sub_dirs):
        with scandir(sub_dirs[i][0]) as dirs:
            for entry in dirs:
                if entry.is_dir():
                    sub_dirs.append((entry.path, sub_dirs[i][1]+((entry.name+"-") if entry.name != "villager" else "")))
                elif entry.is_file() and entry.name.endswith(".json"):
                    with open(entry.path, "r") as f:
                        clothing_attributes[sub_dirs[i][1]+entry.name[:-5]] = json.loads(repair_json(f.read()))
                    if gen_cleaned_jsons:
                        path=output_path + "/generated/cleaned_jsons/"+"/".join(sub_dirs[i][1].split("-"))
                        if not Path(path).exists():
                            Path(path).mkdir(parents=True, exist_ok=True)
                        with open(path+entry.name, "x", encoding="utf-8") as fi:
                            fi.write(json.dumps(clothing_attributes[sub_dirs[i][1]+entry.name[:-5]], indent=4))
        i+=1
    if gen_cleaned_jsons:
        with open(output_path + "/generated/cleaned_jsons/_combined.json", "x", encoding="utf-8") as f:
            f.write(json.dumps(clothing_attributes, indent=4))


def get_attributes(item:str):
    global test_var
    if "test_var" not in globals():
        test_var=set()
    split = item.replace("butterflypin", "emblem-butterflypin").split("-")
    attributes={}
    for i in range(2, len(split)+1):
        if "-".join(split[1:i]) in clothing_attributes:
            attributes["category"] = "-".join(split[1:i])
            break
    if not attributes: return

    ### This intentionally ignores cases where there is no value in a specific type but would get one from "*",
    ### as that is true to the game. The game checks in this order, breaking even when not everything is set:
    """
        ...["attributes"]["warmthByType"][<regex>] = <int>
        ...["attributesByType"][<regex>]["warmth"] = <int>
        ...["attributes"]["warmth"] = <int>
    """

    ### Warmth
    if "attributes" in clothing_attributes[attributes["category"]] and\
            "warmthByType" in clothing_attributes[attributes["category"]]["attributes"]:
        if debug:
            [test_var.add("attributes: "+attribute) for attribute in clothing_attributes[attributes["category"]]["attributes"]] ### DEBUG
        for regex in clothing_attributes[attributes["category"]]["attributes"]["warmthByType"]:
            if re.match(regex, item):
                attributes["warmth"]=clothing_attributes[attributes["category"]]["attributes"]["warmthByType"][regex]
                break
    elif "attributesByType" in clothing_attributes[attributes["category"]]:
        for regex in clothing_attributes[attributes["category"]]["attributesByType"]:
            if debug:
                [test_var.add("attributesByType: "+attribute) for attribute in clothing_attributes[attributes["category"]]["attributesByType"][regex]] ### DEBUG
            if re.match(regex, item) and "warmth" in clothing_attributes[attributes["category"]]["attributesByType"][regex]:
                attributes["warmth"] = clothing_attributes[attributes["category"]]["attributesByType"][regex]["warmth"]
                break
    elif "attributes" in clothing_attributes[attributes["category"]] and\
            "warmth" in clothing_attributes[attributes["category"]]["attributes"]:
        if debug:
            [test_var.add("attributes: "+attribute) for attribute in clothing_attributes[attributes["category"]]["attributes"]] ### DEBUG
        attributes["warmth"] = clothing_attributes[attributes["category"]]["attributes"]["warmth"]

    ### RainProt
    if "attributes" in clothing_attributes[attributes["category"]] and\
            "rainProtectionPercByType" in clothing_attributes[attributes["category"]]["attributes"]:
        if debug:
            [test_var.add("attributes: "+attribute) for attribute in clothing_attributes[attributes["category"]]["attributes"]] ### DEBUG
        for regex in clothing_attributes[attributes["category"]]["attributes"]["rainProtectionPercByType"]:
            if re.match(regex, item):
                attributes["rainProtectionPerc"]=clothing_attributes[attributes["category"]]["attributes"]["rainProtectionPercByType"][regex]
                break

    ### EyeProt
    if "attributesByType" in clothing_attributes[attributes["category"]]:
        for regex in clothing_attributes[attributes["category"]]["attributesByType"]:
            if debug:
                [test_var.add("attributesByType: "+attribute) for attribute in clothing_attributes[attributes["category"]]["attributesByType"][regex]] ### DEBUG
            if re.match(regex, item) and "eyeprotective" in clothing_attributes[attributes["category"]]["attributesByType"][regex]:
                attributes["eyeprotective"] = clothing_attributes[attributes["category"]]["attributesByType"][regex]["eyeprotective"]
                break


    return attributes























