import json
from util_traders.script import traders_json as traders, translate_trader
from os import mkdir

def generate_tables(install_path:str, *, output_path:str="./"):
    with open(install_path+"/assets/game/lang/en.json", "r") as f:
        lang_dict=json.load(f)

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

    for trader in traders:
        for sold in traders[trader]["selling"]["list"]:
            if sold["code"].startswith("clothes-"):
                if not sold["code"] in sold_by:
                    sold_by[sold["code"]] = []
                    sold_for[sold["code"]] = []
                sold_by[sold["code"]].append(translate_trader(install_path, trader))
                sold_for[sold["code"]].append(f"{sold["price"]["avg"]-sold["price"]["var"]} - {sold["price"]["avg"]+sold["price"]["var"]}")

        for bought in traders[trader]["buying"]["list"]:
            if bought["code"].startswith("clothes-"):
                if not bought["code"] in bought_by:
                    bought_by[bought["code"]] = []
                    bought_for[bought["code"]] = []
                bought_by[bought["code"]].append(translate_trader(install_path, trader))
                bought_for[bought["code"]].append(f"{bought["price"]["avg"]-bought["price"]["var"]} - {bought["price"]["avg"]+bought["price"]["var"]}")

    out='''\
{|<!--
This tables layout was generated automatically via https://github.com/BlackberryMuffin/vs-wiki-table-generator. If you want to modify this tables layout, consider changing the code directly instead the table\'s source text!
-->class="wikitable sortable mw-collapsible"
|+<translate>Clothing</translate>||-;
!<translate>Item icon</translate>!!<translate>Item name</translate>!!<translate>Sold by</translate>!!<translate>Sold for (in Rusty Gears)</translate>!!<translate>Purchased by</translate>!!<translate>Purchased for (in Rusty Gears)</translate>!!<translate>Craftable by all</translate>!!<translate>Recipe</translate>
|-'''

    for item in items:
        out+=f"|[[File:{item}.png|64px]]||<translate>{items[item]}</translate>||{f"<translate>{";<br>".join(sold_by[item])}</translate>||{";<br>".join(sold_for[item])}" if item in sold_by else "||"}||{f"<translate>{";<br>".join(bought_by[item])}</translate>||{";<br>".join(bought_for[item])}" if item in bought_by else "||"}||||\n|-\n"
    out+="|}"

    mkdir(output_path+"/generated")
    with open(output_path+"/generated/table.txt", "x") as f:
        f.write(out)
