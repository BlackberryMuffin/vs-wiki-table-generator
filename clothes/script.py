import json
from util_traders.script import traders_json as traders, translate_trader
from os import mkdir

"""
    Seperately from "generated/table.txt", the script will produce "generated/translation_help.txt".
    If its content has not yet been placed in the wiki page of the table, it is to be placed below the <languages/> tag at the top of the page.
    Without it, this table will not translate properly.
        It can technically be anywhere, but this placement reduces the risk of it being deleted by accident.
"""


special_names=["nadiya"]
interpret_as={"butterflypin":"emblem"}
def generate_tables(install_path:str, *, output_path:str="./"):
    mkdir(output_path+"/generated")
    with open(install_path+"/assets/game/lang/en.json", "r") as f:
        lang_dict=json.load(f)

    item_categories={}
    items={}
    descriptions={}
    sold_by={}
    sold_for={}
    bought_by={}
    bought_for={}

    for key in lang_dict:
        if key.startswith(("item-clothes-")):
            items[key[5:]] = lang_dict[key]

        if key.startswith(("itemdesc-clothes-")):
            descriptions[key[9:]] = lang_dict[key]

    trans_help=["<!--This is here for easier translation of the table using Tunit. Do not touch this if you don't know what you're doing!-->", "{{Hovertip||"]
    trader_names=[]
    for trader in traders:
        trader_names.append((trader, translate_trader(install_path, trader)))
        for sold in traders[trader]["selling"]["list"]:
            if sold["code"].startswith("clothes-"):
                if not sold["code"] in sold_by:
                    sold_by[sold["code"]] = []
                    sold_for[sold["code"]] = []
                sold_by[sold["code"]].append(translate_trader(install_path, trader, addTunit=True))
                sold_for[sold["code"]].append(f"{sold["price"]["avg"]-sold["price"]["var"]} - {sold["price"]["avg"]+sold["price"]["var"]}")

        for bought in traders[trader]["buying"]["list"]:
            if bought["code"].startswith("clothes-"):
                if not bought["code"] in bought_by:
                    bought_by[bought["code"]] = []
                    bought_for[bought["code"]] = []
                bought_by[bought["code"]].append(translate_trader(install_path, trader, addTunit=True))
                bought_for[bought["code"]].append(f"{bought["price"]["avg"]-bought["price"]["var"]} - {bought["price"]["avg"]+bought["price"]["var"]}")
    trans_help += [f"<translate><!--T:{trader[0]}--> {trader[1]}</translate>" for trader in trader_names] + ["}}", trans_help[0]]



    out='''\
{|<!--
This tables layout was generated automatically via https://github.com/BlackberryMuffin/vs-wiki-table-generator. If you want to modify this tables layout, consider changing the code directly instead the table\'s source text!
-->class="wikitable sortable mw-collapsible"
|+<translate>Clothing</translate>||-;
!<translate>Item ccon</translate>!!<translate>Item name</translate>!!<translate>Item description</translate>!!<translate>Sold by</translate>!!<translate>Sold for (in rusty gears)</translate>!!<translate>Purchased by</translate>!!<translate>Purchased for (in rusty gears)</translate>!!<translate>Craftable by all</translate>!!<translate>Recipe</translate>
|-'''

    for item in items:
        out+=f"|[[File:{item}.png|64px]]||<translate>{items[item]}</translate>||{f"<translate>{descriptions[item]}</translate>" if item in descriptions else ""}||{f"{";<br>".join(sold_by[item])}||{";<br>".join(sold_for[item])}" if item in sold_by else "||"}||{f"{";<br>".join(bought_by[item])}||{";<br>".join(bought_for[item])}" if item in bought_by else "||"}||||\n|-\n"
        #out+=f"|[[File:{item}.png|64px]]||{items[item]}||{f"{";<br>".join(sold_by[item])}||{";<br>".join(sold_for[item])}" if item in sold_by else "||"}||{f"{";<br>".join(bought_by[item])}||{";<br>".join(bought_for[item])}" if item in bought_by else "||"}||||\n|-\n"
    out+="|}"

    with open(output_path+"/generated/table.txt", "x") as f:
        f.write(out)
    with open(output_path+"/generated/translation_help.txt", "x") as f:
        f.write("\n".join(trans_help))
