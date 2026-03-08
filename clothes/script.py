import json
from util_traders.script import traders_json as traders, translate_trader
from os import mkdir
from _util_general.mediawiki_templates import tunit, hovertip

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
def generate_tables(install_path:str, *, output_path:str="./"):
    mkdir(output_path+"/generated")
    with open(install_path+"/assets/game/lang/en.json", "r") as f:
        lang_dict=json.load(f)

    debug = True

    items={}
    warmth={}
    rain_prot={}
    eye_prot={}
    descriptions={}
    sold_by={}
    bought_by={}
    craftable={}

    ### Debug TODO: Remove this
    if debug:
        items["example-entry"]="Example entry"; warmth["example-entry"]="0%"; rain_prot["example-entry"]="0%"; eye_prot["example-entry"]="0%";
        descriptions["example-entry"]="This item is a placeholder which fills out all the columns so my code doesn't trim them off'"; sold_by["example-entry"]=["Null trader"]; bought_by["example-entry"]=["Null trader"]; craftable["example-entry"]="''yes''<br>only by Example Classes";

    for key in lang_dict:
        if key.startswith(("item-clothes-")):
            items[key[5:]] = lang_dict[key]

        if key.startswith(("itemdesc-clothes-")):
            descriptions[key[9:]] = lang_dict[key]

    trans_help=["<!--This is here for easier translation of the table using Tunit. Do not touch this if you don't know what you're doing!-->", "{{Hovertip||"]
    trader_names=[]
    contains_villagers=[0]
    very_specific_function = lambda trader, sold_or_bought: hovertip(translate_trader(install_path, trader, addTunit=True, villagerCounter=contains_villagers), f"{sold_or_bought["price"]["avg"]-sold_or_bought["price"]["var"]} - {sold_or_bought["price"]["avg"]+sold_or_bought["price"]["var"]} {{{{Tunit|item-gear-rusty|rusty gears}}}}")

    for trader in traders:
        trader_names.append((trader, translate_trader(install_path, trader)))
        for sold in traders[trader]["selling"]["list"]:
            if sold["code"].startswith("clothes-"):
                if not sold["code"] in sold_by:
                    sold_by[sold["code"]] = []
                sold_by[sold["code"]].append(very_specific_function(trader, sold))

        for bought in traders[trader]["buying"]["list"]:
            if bought["code"].startswith("clothes-"):
                if not bought["code"] in bought_by:
                    bought_by[bought["code"]] = []
                bought_by[bought["code"]].append(very_specific_function(trader, sold))
    tunit_entries = special_tunit_entries + trader_names
    trans_help += [f"<translate><!--T:{entry[0]}--> {entry[1]}</translate>" for entry in tunit_entries] + ["}}", trans_help[0]]



    out=""+\
        "{|<!--\n"+\
        "This tables layout was generated automatically via https://github.com/BlackberryMuffin/vs-wiki-table-generator. If you want to modify this tables layout, consider changing the code directly instead the table's source text!\n"+\
        '-->class="wikitable sortable mw-collapsible" style="text-align:center;"\n'+\
        "|+<translate>Clothing</translate>||-;"+\
        "\n"+\
        "!<translate>Item icon</translate>"+\
        "!!<translate>Item name</translate>"+\
        ("!!<translate>Warmth</translate>" if len(warmth) != 0 else "")+\
        ("!!<translate>Rain prot.</translate>" if len(rain_prot) != 0 else "")+\
        ("!!<translate>Eye prot.</translate>" if len(eye_prot) != 0 else "")+\
        ("!!<translate>Item description</translate>" if len(descriptions) != 0 else "")+\
        ("!!<translate>Bought from</translate>" if len(sold_by) != 0 else "")+\
        ("!!<translate>Sold to</translate>" if len(bought_by) != 0 else "")+\
        ("!!<translate>Craftable</translate>" if len(craftable) != 0 else "")+\
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


    with open(output_path+"/generated/table.txt", "x") as f:
        f.write(out)
    with open(output_path+"/generated/translation_help.txt", "x") as f:
        f.write("\n".join(trans_help))
