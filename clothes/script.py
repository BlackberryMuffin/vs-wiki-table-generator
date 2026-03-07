import json
from util_traders.script import traders_json as traders, translate_trader
from os import mkdir

def generate_tables(install_path:str, *, output_path:str="./"):
    with open(install_path+"/assets/game/lang/en.json", "r") as f:
        lang_dict=json.load(f)

    items={}
    descriptions={}
    sold_by={}
    bought_by={}
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
                sold_by[sold["code"]].append(translate_trader(install_path, trader))

        for bought in traders[trader]["buying"]["list"]:
            if bought["code"].startswith("clothes-"):
                if not bought["code"] in bought_by:
                    bought_by[bought["code"]] = []
                bought_by[bought["code"]].append(translate_trader(install_path, trader))

    out='{|<!--\nThis tables layout was generated automatically via https://github.com/BlackberryMuffin/vs-wiki-table-generator. If you want to modify this tables layout, consider changing the code directly instead the table\'s source text!\n-->class="wikitable sortable mw-collapsible"\n|+<translate>Clothing</translate>||-;\n!<translate>Item icon</translate>!!<translate>Item name</translate> !! <translate>Sold by</translate> !! <translate>Purchased by</translate> !! <translate>Craftable by all</translate> !! <translate>Recipe</translate>\n|-'
    for item in items:
        out+=f"|[[File:{item}.png|64px]]||<translate>{items[item]}</translate>||{f"<translate>{"\n".join(sold_by[item])}</translate>" if item in sold_by else ""}||{f"<translate>{"\n".join(bought_by[item])}</translate>" if item in bought_by else ""}||||\n|-\n"
    out+="|}"

    mkdir(output_path+"/generated")
    with open(output_path+"/generated/table.txt", "x") as f:
        f.write(out)
