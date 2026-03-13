import json
import util_traders.script as trader_util
from pathlib import Path
from _util_general.mediawiki_templates import tunit, hovertip
from _util_general.lang_dicts import get_dict
from _util_general.json_util import repair as repair_json
from os import scandir
import re

from util_recipes.script import recipes_by_type

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
    Path(output_path+"/generated/recipes").mkdir(parents=True, exist_ok=True)

    lang_dict=get_dict(install_path, lang=lang)
    gen_clothing_attributes(install_path, output_path, gen_cleaned_jsons=True)

    categories_ignore=["nadiya"]
    categories_replace={"butterflypin": "emblem"}
    categories={"_all":[]}

    items={}
    warmth={}
    rain_prot={}
    eye_prot={}
    descriptions={}
    sold_by={}
    bought_by={}
    craftable={}

    recipes = crafting_help(install_path, output_path, lang_dict)


    # Fills `items` (used for item-id + item name) and `descriptions` (used for item lore text) from the games translation files
    for key in lang_dict:
        if key.startswith("item-clothes-"):
            items[key[5:]] = f"<translate>{(lang_dict if key in lang_dict else lang_dict)[key]}</translate>"

        if key.startswith("itemdesc-clothes-"):
            descriptions[key[9:]] = f"<translate>{(lang_dict if key in lang_dict else lang_dict)[key].replace('<font color="#99c9f9">', '<font color="#0099ff">')}</translate>"

    for recipe in recipes:
        #craftable[recipe] = ",<br>".join([str(list(recipes[recipe][i]["ingredients"].keys())) for i in range(len(recipes[recipe]))])
        string = ",and<br>".join({"by "+ recipes[recipe][i]["requiresTrait"]+"s" for i in range(len(recipes[recipe])) if "requiresTrait" in recipes[recipe][i]})
        craftable[recipe] = "yes" + (",<br>" if string else "") + string
        if recipe not in items:
            #items[recipe] = f"{recipe}<sup>{len(annotations)+1}</sup>"
            items[recipe] = f"{recipe}<sup>_-XYZ-_</sup>"

    for item in items:
        split_name = item.split("-")
        for i in range(1, len(split_name)):
            category = split_name[i]
            if category in categories_ignore:
                continue
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
            categories["_all"].append(item)

            break
    for replacee in categories_replace:
        if replacee not in categories:
            continue
        if categories_replace[replacee] not in categories:
            categories[categories_replace[replacee]] = []
        categories[categories_replace[replacee]] += categories[replacee]
        del categories[replacee]
    with open(output_path+"/generated/categories.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(categories, indent=4))


    # Fills `warmth`, `rain_prot`, and `eye_prot` (no clue what the latter 2 do tbh)
    for item in items:
        attributes = get_attributes(item)
        if attributes is None:
            continue
        if "warmth" in attributes and attributes["warmth"]:
            warmth[item] = f"{attributes["warmth"]}°C"
        if "rainProtectionPerc" in attributes and attributes["rainProtectionPerc"]:
            rain_prot_tmp = attributes["rainProtectionPerc"]*100
            rain_prot[item] = f"{int(rain_prot_tmp) if rain_prot_tmp==int(rain_prot_tmp) else rain_prot_tmp}%"
        if "eyeprotective" in attributes and attributes["eyeprotective"]:
            eye_prot[item] = "✅" ### <-- In case your font doesn't support it, that's a green checkmark :D

    test_var_out = list(test_var)
    test_var_out.sort()
    if debug:
        with open(output_path+"generated/attributes", "x", encoding="utf-8") as f:
            f.write("\n".join(test_var_out))

    # A lambda function which generates a string like "{{Hovertip|{{Tunit|trader-treasurehunter|Treasure hunter trader}}|1.5 - 2.5 {{Tunit|item-gear-rusty|rusty gears}}}}" from trade information
    contains_villagers=[0]
    very_specific_function = lambda trader, trade: hovertip(trader_util.translate_trader(install_path, trader, addTunit=True, villagerCounter=contains_villagers), f"{trade["price"]["avg"]-trade["price"]["var"]} - {trade["price"]["avg"]+trade["price"]["var"]} {{{{Tunit|item-gear-rusty|rusty gears}}}}")
    # Fetches all clothing trades from trader_util
    trades = trader_util.trades_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))
    # The previously fetched trade data is now modified using very_specific_function and then added `sold_by` and `bought_by` which hold readable trade information
    for clothing in trades:
        villager_count=contains_villagers[0]
        sold_by[clothing] = ([very_specific_function(*trade) for trade in trades[clothing]["selling"]], villager_count!=contains_villagers)
        villager_count=contains_villagers[0]
        bought_by[clothing] = ([very_specific_function(*trade) for trade in trades[clothing]["buying"]], villager_count!=contains_villagers)




    sorted_categories=list(categories.keys())
    sorted_categories.sort()
    for category in sorted_categories:
        tmp = categories[category]
        del categories[category]
        categories[category] = tmp


    annotations = {
        "no_name": "<translate>This item is not yet present in <code>assets/game/lang/en.json</code>, so it has no official name yet.</translate>",
        "villager": "<translate>Villagers, while similar to {{ll|Trading|traders}} are seperate. At the risk of spoiling the game's story, see {{ll|Villager}} and/or {{ll|Village}} if you want to learn more.</translate>",
    }

    references = {
        "icon": ['<ref name="icon"><br><code>.blockitempngexport all 400</code></ref>'],
        "lang": ['<ref name="lang"><br><code>assets/game/lang/</code></ref>'],
        "warmth": ['<ref name="attribute"><br><code>assets/survival/itemtypes/wearable/seraph/</code></ref>'],
        "rain_prot": ['<ref name="attribute"><br><code>assets/survival/itemtypes/wearable/seraph/</code></ref>', '<ref name="rain_prot_unused"><br>as of <code>1.22.0</code> the rain prot. stat is not used or shown ingame</ref>'],
        "eye_prot": ['<ref name="attribute"><br><code>assets/survival/itemtypes/wearable/seraph/</code></ref>', '<ref name="eye_prot_unused"><br>as of <code>1.22.0</code> the eye prot. stat is not used or shown ingame</ref>'],
        "trades": ['<ref name="trades"><br><code>assets/survival/config/tradelists/</code></ref>'],
        "crafting": ['<ref name="crafting"><br><code>assets/survival/recipes/grid/clothes/</code></ref>'],
    }
    def get_ref(ref_str:str):
        yield "".join(references[ref_str])
        print(ref_str, "".join(references[ref_str]))
        for i in range(len(references[ref_str])):
            pass#references[ref_str][i] = re.sub(r'<ref name="([^"\n]*)">.*', r'<ref name="\1" />', references[ref_str][i])


    combined_tables = []
    for category in categories:
        annot_bools = {
        "villager": False,
        "no_name": False,
        }

        has_warmth = False
        has_rain_prot = False
        has_eye_prot = False
        has_descriptions = False
        has_sold_by = False
        has_bought_by = False
        has_craftable = False

        for item in categories[category]:
            has_warmth +=  item in warmth
            has_rain_prot +=  item in rain_prot
            has_eye_prot +=  item in eye_prot
            has_descriptions +=  item in descriptions
            if item in sold_by:
                has_sold_by += 1
                annot_bools["villager"] += sold_by[item][1]
            if item in bought_by:
                has_bought_by += 1
                annot_bools["villager"] += bought_by[item][1]
            has_craftable +=  item in craftable
            annot_bools["no_name"] += items[item] == item
            
        annotations_inner = []
        for annotation in annotations:
            if annot_bools[annotation]:
                annotations_inner.append(annotations[annotation])
                annot_bools[annotation] = str(len(annotations_inner)-1)


        out=f"=== <translate>{category.title()}</translate> ===\n"+\
            '{|<!--\n'+\
            "This tables layout was generated automatically via https://github.com/BlackberryMuffin/vs-wiki-table-generator. If you want to modify this tables layout, consider changing the code directly instead the table's source text!\n"+\
            '-->class="mw-collapsible mw-collapsed""\n'+\
            '|+\n'+\
            '|\n'+\
            '{|class="wikitable sortable" style="text-align:center;\n'+\
            f"|+||-;"+\
            "\n"+\
            f'!<translate>Item icon</translate>{list(get_ref("icon"))[0]}'+\
            f'!!<translate>Item name</translate>{list(get_ref("lang"))[0]}'+\
            (f'!!data-sort-type="number"|<translate>Warmth</translate>{list(get_ref("warmth"))[0]}' if has_warmth != 0 else "")+\
            (f'!!data-sort-type="number"|<translate>Rain prot.</translate>{list(get_ref("rain_prot"))[0]}' if has_rain_prot != 0 else "")+\
            (f'!!<translate>Eye prot.</translate>{list(get_ref("eye_prot"))[0]}' if has_eye_prot != 0 else "")+\
            (f'!!<translate>Item description</translate>{list(get_ref("lang"))[0]}' if has_descriptions != 0 else "")+\
            (f'!!<translate>Bought from</translate>{list(get_ref("trades"))[0]}' if has_sold_by != 0 else "")+\
            (f'!!<translate>Sold to</translate>{list(get_ref("trades"))[0]}' if has_bought_by != 0 else "")+\
            (f'!!<translate>Craftable</translate>{list(get_ref("crafting"))[0]}' if has_craftable != 0 else "")+\
            '\n'+\
            '|-\n'

        for item in categories[category]:

            out+=""+\
                f"|[[File:{item}.png|64px]]"+\
                f"||{items[item].replace("_-XYZ-_", "" if not annot_bools["no_name"] else annot_bools["no_name"])}"+\
                (f"||{f"{warmth[item]}" if item in warmth else ""}" if has_warmth != 0 else "")+\
                (f"||{f"{rain_prot[item]}" if item in rain_prot else ""}" if has_rain_prot != 0 else "")+\
                (f"||{f"{eye_prot[item]}" if item in eye_prot else ""}" if has_eye_prot != 0 else "")+\
                (f"||{f"{descriptions[item]}" if item in descriptions else ""}" if has_descriptions != 0 else "")+\
                (f"||{f"{",<br>".join(sold_by[item][0]).replace("_-XYZ-_", "" if not annot_bools["villager"] else annot_bools["villager"])}" if item in sold_by else ""}" if has_sold_by != 0 else "")+\
                (f"||{f"{",<br>".join(bought_by[item][0]).replace("_-XYZ-_", "" if not annot_bools["villager"] else annot_bools["villager"])}" if item in bought_by else ""}" if has_bought_by != 0 else "")+\
                (f"||{f"<translate>{craftable[item]}</translate>" if item in craftable else ""}" if has_craftable != 0 else "")+\
                "\n|-\n"
        out+=""+\
            "|}"+\
            "<br>".join([f"<sup>{i+1}</sup>{annotations_inner[i]}" for i in range(len(annotations_inner))])+\
            "\n|}"

        if category != "_all":
            combined_tables.append(out)

        with open(output_path+f"/generated/tables/{category}.txt", "x", encoding="utf-8") as f:
            f.write(out)

    with open(output_path+"/generated/tables/_combined.txt", "x", encoding="utf-8") as f:
        f.write(("\n"*3).join(combined_tables))

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


def crafting_help(install_path:str, output_path:str, lang_dict):
    specials = {
        "color": [w[11:] for w in lang_dict if w.startswith("item-cloth-")]
    }

    ### TODO: finish craftables
    recipes = recipes_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))
    replace = {}
    for clothing in recipes:
        if re.search(r"(\{.*})", clothing):
            replace[clothing] = {}
            clothing_copy = clothing
            s = re.search(r"(\{.*})", clothing_copy)
            while s:
                wild_card = s[0][1:-1]
                if s:
                    new = None
                    for sub_recipe in recipes[clothing]:
                        if "allowedVariants" in sub_recipe and wild_card in sub_recipe["allowedVariants"]:
                            clothing_copy = clothing_copy.replace(s[0], "")
                            new = sub_recipe["allowedVariants"][wild_card]
                        elif wild_card in specials:
                            clothing_copy = clothing_copy.replace(s[0], "")
                            new = specials[wild_card]
                            if "skipVariants" in sub_recipe and wild_card in sub_recipe["skipVariants"]:
                                new = [n for n in new if n not in sub_recipe["skipVariants"][wild_card]]
                        else:
                            for ingredient in sub_recipe["ingredients"]:
                                if sub_recipe["ingredients"][ingredient]["name"] == wild_card:
                                    clothing_copy = clothing_copy.replace(s[0], "")
                                    new = sub_recipe["ingredients"][ingredient]["allowedvariants"]
                    replace[clothing][s[0]] = new
                s = re.search(r"(\{.*})", clothing_copy)

    with open(output_path + "/generated/recipes/wild_cards.json", "x", encoding="utf-8") as f:
        f.write(json.dumps([clothing for clothing in replace], indent=4))

    ### DEBUG addition, just tests the warning system
    replace["fake-{wild}-{card}-item, this is just a drill!"] = 1
    for clothing in replace:
        if re.search(r"(.*\{[^}]*})(.*\{[^}]*})+.*", clothing):
            print("\t\tPANIC: THERE IS A CLOTHING RECIPE WITH MORE THAN ONE WILD CARD!!! IT IS:\t", clothing)
            continue
        for replacee in replace[clothing]:
            for replacement in replace[clothing][replacee]:
                name = clothing.replace(replacee, replacement)
                recipes[name] = json.loads(json.dumps(recipes[clothing]))
                for sub_recipe in recipes[name]:
                    for ingredient in sub_recipe["ingredients"]:
                        if "code" in sub_recipe["ingredients"][ingredient] and replacee in \
                                sub_recipe["ingredients"][ingredient]["code"]:
                            tmp = sub_recipe["ingredients"][ingredient]
                            tmp["code"] = tmp["code"].replace(replacee, replacement)
        del recipes[clothing]

    with open(output_path + "/generated/recipes/main.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(recipes, indent=4))

    multi = []
    fakes = []
    for recipe in recipes:
        if not recipe.startswith("clothes-"):
            fakes.append(recipe)
        elif len(recipes[recipe]) > 1:
            multi.append(recipe)
    with open(output_path + "/generated/recipes/fake.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(fakes, indent=4))
    with open(output_path + "/generated/recipes/multi.json", "x", encoding="utf-8") as f:
        f.write(json.dumps(multi, indent=4))
    return {recipe:recipes[recipe] for recipe in recipes if recipe not in fakes}




















