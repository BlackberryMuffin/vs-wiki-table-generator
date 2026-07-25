from scripts._util_general.file_util import read_file, write_file, write_file_safe
from scripts._util_general.mediawiki_templates import tunit, hovertip
from scripts.util_0lang.script import get_dict
import re
from scripts.util_char_classes.script import char_class_gear_by_type
from scripts.util_fishing_junk.script import fishable_by_type
from scripts.util_loot.script import lootable_by_type
from scripts.util_panning.script import pannable_by_type
import scripts.util_traders.script as trader_util
from scripts.clothes.de_clutter import get_test_var, gen_clothing_attributes, get_attributes, crafting_help, get_old_t_ids

debug = True

"""
    Seperately from "generated/table.txt", the script will produce "generated/translation_help.txt".
    If its content has not yet been placed in the wiki page of the table, it is to be placed below the <languages/> tag at the top of the page.
    Without it, this table will not translate properly.
        It can technically be anywhere, but this placement reduces the risk of it being deleted by accident.
"""



def generate(install_path:str, *, output_path:str="./", lang:str="en"):

    lang_dict=get_dict(lang=lang)
    gen_clothing_attributes(install_path, output_path, debug, gen_cleaned_jsons=True)

    special_tunit_entries = {
        "item-gear-rusty": "rusty gears",

        "class-equipment-commoner": "Part of the '''Commoner''' starter gear",
        "class-equipment-hunter": "Part of the '''Hunter''' starter gear",
        "class-equipment-malefactor": "Part of the '''Malefactor''' starter gear",
        "class-equipment-clockmaker": "Part of the '''Clockmaker''' starter gear",
        "class-equipment-blackguard": "Part of the '''Blackguard''' starter gear",
        "class-equipment-tailor": "Part of the '''Tailor''' starter gear",

        "table-header-icon": "Item icon",
        "table-header-name": "Item name",
        "table-header-warmth": "Warmth",
        "table-header-rain-prot": "Rain prot.",
        "table-header-eye-prot": "Eye prot.",
        "table-header-desc": "Item description",
        "table-header-bought-from": "Bought from",
        "table-header-sold-to": "Sold to",
        "table-header-craftable": "Craftable",
        "table-header-lootpool": "Present in stackrandomizers",
        "table-header-other-means": "Other means of obtaining",

        "table-content-clothier-only": "Requires Clothier trait",
        "table-content-panning-bonysoil": "Obtainable from panning bony soil",
        "table-content-panning-other": "Obtainable from panning gravel or sand",
        "table-content-fishing-junk": "Obtainable from fishing",
        "title-tables": "Tables",
        "title-columns": "Columns",
    }

    old_t_ids=get_old_t_ids(output_path+"/re_input/")

    categories_ignore=["nadiya"]
    categories_replace={"butterflypin": "emblem"}
    categories={"--all":[]}
    lbt=lootable_by_type(lambda item: item.startswith("clothes-"))
    pan=pannable_by_type(lambda item: item.startswith("clothes-"))
    fish=fishable_by_type(lambda item: item.startswith("clothes-"))
    char=char_class_gear_by_type(lambda item: item.startswith("clothes-"))

    round_to=3

    items={}
    warmth={}
    rain_prot={}
    eye_prot={}
    descriptions={}
    sold_by={}
    bought_by={}
    craftable={}
    lootable={item: ",<br>".join([f"<code>{hovertip(arr[0][3:], f"{round(arr[1] * 100, round_to)}%")}</code>" for arr in lbt[item]]) for item in lbt}
    other_means={}


    pannable={item: ",<br>".join([f"{hovertip(arr[0], f"{round(arr[1] * 100, round_to)}%")}" for arr in pan[item]]) for item in pan}
    fishable={item: hovertip(tunit("table-content-fishing-junk", special_tunit_entries["table-content-fishing-junk"]), f"{round(fish[item]*100, round_to)}%") for item in fish}
    starter_gear={item: ",<br>".join([tunit(char_class, special_tunit_entries[char_class]) for char_class in char[item]]) for item in char}

    write_file(output_path+"/generated/lootable.json", lootable, encode_json=True)

    write_file(output_path+"/generated/pannable.json", pannable, encode_json=True)
    write_file(output_path+"/generated/fishable.json", fishable, encode_json=True)
    write_file(output_path+"/generated/class_obtainable.json", starter_gear, encode_json=True)


    recipes = crafting_help(install_path, output_path, lang_dict)

    # Fills `items` (used for item-id + item name) and `descriptions` (used for item lore text) from the games translation files
    for key in lang_dict:
        if key.startswith("item-clothes-"):
            items[key[5:]] = f"<translate>{old_t_ids[key[5:]]["name"] if key[5:] in old_t_ids else ""}{(lang_dict if key in lang_dict else lang_dict)[key]}</translate>"

        if key.startswith("itemdesc-clothes-"):
            descriptions[key[9:]] = f"<translate>{old_t_ids[key[9:]]["desc"] if key[9:] in old_t_ids else ""}{(lang_dict if key in lang_dict else lang_dict)[key].replace('<font color="#99c9f9">', '<font color="#0099ff">')}</translate>"

    # add recipes
    for recipe in recipes:
        string = "✅" ### <-- In case your font doesn't support it, that's a green checkmark :D
        for i in range(len(recipes[recipe])):
            if "requiresTrait" in recipes[recipe][i]:
                if recipes[recipe][i]["requiresTrait"] != "clothier":
                    raise Exception(f"ERROR: THERE IS A NON-CLOTHIER CRAFTING REQUIREMENT\nTHE CODE MUST BE CHANGED ACCORDINGLY")
                string = f"❎<br>{tunit("table-content-clothier-only",special_tunit_entries["table-content-clothier-only"])}"

        # if item in recipes but not in en.json: add it
        craftable[recipe] = string
        if recipe not in items:
            items[recipe] = f"{recipe}<sup>_-XYZ-_</sup>"

    for item in items:
        s = ",<br>".join([fishable[junk] for junk in fishable if junk == item] + [pannable[mud] for mud in pannable if mud == item] + [starter_gear[gear] for gear in starter_gear if gear == item])
        if s:
            other_means[item]=s

    # Sort into clothing categories
    for item in items:
        split_name = item.split("-")
        for i in range(1, len(split_name)):
            category = split_name[i]
            if category in categories_ignore:
                continue
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
            categories["--all"].append(item)

            break
    for replacee in categories_replace:
        if replacee not in categories:
            continue
        if categories_replace[replacee] not in categories:
            categories[categories_replace[replacee]] = []
        categories[categories_replace[replacee]] += categories.pop(replacee)
    write_file(output_path+"/generated/categories.json", categories, encode_json=True)


    # Fills `warmth`, `rain_prot`, and `eye_prot` (no clue what the latter 2 do tbh)
    for item in items:
        attributes = get_attributes(item, debug)
        if attributes is None:
            continue
        if "warmth" in attributes and attributes["warmth"]:
            warmth[item] = f"{attributes["warmth"]}°C"
        if "rainProtectionPerc" in attributes and attributes["rainProtectionPerc"]:
            rain_prot_tmp = attributes["rainProtectionPerc"]*100
            rain_prot[item] = f"{int(rain_prot_tmp) if rain_prot_tmp==int(rain_prot_tmp) else rain_prot_tmp}%"
        if "eyeprotective" in attributes and attributes["eyeprotective"]:
            eye_prot[item] = "✅" ### <-- In case your font doesn't support it, that's a green checkmark :D

    test_var_out = list(get_test_var())
    test_var_out.sort()
    if debug:
        write_file(output_path+"generated/attributes", "\n".join(test_var_out), encode_json=False)

    # A lambda function which generates a string like "{{Hovertip|{{Tunit|trader-treasurehunter|Treasure hunter trader}}|1.5 - 2.5 {{Tunit|item-gear-rusty|rusty gears}}}}" from trade information
    contains_villagers=[0]
    very_specific_function = lambda trader, trade: hovertip(trader_util.translate_trader(install_path, trader, addTunit=True, villagerCounter=contains_villagers), f"{trade["price"]["avg"]-trade["price"]["var"]} - {trade["price"]["avg"]+trade["price"]["var"]} {tunit("item-gear-rusty", special_tunit_entries["item-gear-rusty"])}")
    # Fetches all clothing trades from trader_util
    trades = trader_util.trades_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))
    # The previously fetched trade data is now modified using very_specific_function and then added `sold_by` and `bought_by` which hold readable trade information
    for clothing in trades:
        villager_count=contains_villagers[0]
        sold_by[clothing] = ([very_specific_function(*trade) for trade in trades[clothing]["selling"]], villager_count!=contains_villagers)
        villager_count=contains_villagers[0]
        bought_by[clothing] = ([very_specific_function(*trade) for trade in trades[clothing]["buying"]], villager_count!=contains_villagers)




    sorted_categories=list(categories.keys())
    super_categories={
        "primary-clothing ===": ("head", "shoulder", "upperbody", "upperbodyover", "lowerbody", "foot", "face", "hand", "waist"),
        "pure-accessories ===": ("arm", "emblem", "neck"),
        "citations ==": (),
    }
    sorted_categories.sort()
    used_categories = []
    [(used_categories.append(super_category), used_categories.extend(super_categories[super_category])) for super_category in super_categories]
    for super_category in super_categories:
        categories[super_category] = None
        for category in super_categories[super_category]:
            categories[category] = categories.pop(category)

    tmp = {
        "citation-no-name": 'This item is not yet present in <tvar name="path_name"><code>assets/game/lang/en.json</code></tvar>, so it has no official name yet.',
        "citation-villager": "Villagers, while similar to {{ll|Trading|traders}} are separate. At the risk of spoiling the game's story, see {{ll|Villager}} and/or {{ll|Village}} if you want to learn more.",
    }
    annotations = {
        "no_name": [
            f"<translate><!--T:citation-no-name--> {tmp["citation-no-name"]}</translate>",
            tunit("citation-no-name", tmp["citation-no-name"].replace('<tvar name="path_name">', "").replace("</tvar>", "")),
            False,
        ],
        "villager": [
            f"<translate><!--T:citation-villager--> {tmp["citation-villager"]}</translate>",
            tunit("citation-villager", tmp["citation-villager"]),
            False,
        ],
    }
    def get_ann(ref_str:str, *, force_og:bool=False):
        if force_og:
            return annotations[ref_str][0]
        if annotations[ref_str][2]:
            return annotations[ref_str][1]
        annotations[ref_str][2] = True
        return annotations[ref_str][0]


    references = {
        "icon": [['<ref name="icon"><br><code>.blockitempngexport all 400</code></ref>']],
        "lang": [['<ref name="lang"><br><code>assets/game/lang/</code></ref>']],
        "warmth": [['<ref name="attribute"><br><code>assets/survival/itemtypes/wearable/seraph/</code></ref>']],
        "rain_prot": [['<ref name="attribute"><br><code>assets/survival/itemtypes/wearable/seraph/</code></ref>', '<ref name="rain_prot_unused"><br>as of <code>1.22.0</code> the rain prot. stat is not used or shown ingame</ref>']],
        "eye_prot": [['<ref name="attribute"><br><code>assets/survival/itemtypes/wearable/seraph/</code></ref>', '<ref name="eye_prot_unused"><br>as of <code>1.22.0</code> the eye prot. stat is not used or shown ingame</ref>']],
        "trades": [['<ref name="trades"><br><code>assets/survival/config/tradelists/</code></ref>']],
        "crafting": [['<ref name="crafting"><br><code>assets/survival/recipes/grid/clothes/</code></ref>']],
        "looting": [['<ref name="looting"><br><code>assets/survival/itemtypes/meta/stackrandomizer.json</code></ref>']],
        "other_means": [['<ref name="other_means"><br>{{ll|Class}}: <code>assets/survival/config/characterclasses.json</code><br>{{ll|Panning}}: <code>assets/survival/blocktypes/wood/pan.json</code><br>{{ll|Fishing}}: <code>assets/survival/entities/nonliving/bobber.json</code></ref>']]
    }
    def get_ref(ref_str:str, *, force_og:bool=False):
        return[""]
        yield "".join(references[ref_str][0 if force_og else -1])
        #print(ref_str, "".join(references[ref_str]))
        if not force_og and len(references[ref_str]) == 1:
            references[ref_str].append([])
            for i in range(len(references[ref_str][0])):
                references[ref_str][1].append(re.sub(r'<ref name="([^"\n]*)">.*', r'<ref name="\1"/>', references[ref_str][0][i]))


    combined_tables = []
    csv:str = ""#+"Name, slot, warmth, rain prot, sold to, bought from, recipe type\n"
    for category in categories:
        if category.endswith("="):
            name=category.replace("-", " ").capitalize()
            special_tunit_entries[re.sub(r"(.*) (=+)", r"title-\1", category)] = re.sub(r"(.*) (=+)", r"\1", name)
            combined_tables.append(re.sub(r"(.*) (=+)", r"\2 {{Tunit|_-XYZ-_|\1}} \2", name).replace("_-XYZ-_", re.sub(r"(.*) (=+)", r"title-\1", category)))
            continue
        if category != "--all":
            special_tunit_entries["title-"+category] = category.title()


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
        has_lootable = False
        has_other_means = False

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
            has_lootable +=  item in lootable
            annot_bools["no_name"] += items[item].startswith(item)
            has_other_means += item in other_means

        annotations_inner = []
        for annotation in annotations:
            if annot_bools[annotation]:
                annotations_inner.append(get_ann(annotation, force_og=category=="--all"))
                annot_bools[annotation] = str(len(annotations_inner))

        out=(
                (f"==== {tunit("title-"+category, special_tunit_entries["title-"+category])} ====\n" if category != "--all" else "")+
                '{|<!--\n'
                "This tables layout was generated automatically via https://github.com/BlackberryMuffin/vs-wiki-table-generator. If you want to modify this tables layout, consider changing the code directly instead the table's source text!\n"
                '-->class="mw-collapsible""\n'
                '|+\n'
                '|\n'
                '{|class="wikitable sortable" style="text-align:center;\n'
                f"|+\n"
                "|-"
                "\n"
                f'!{tunit("table-header-icon", special_tunit_entries["table-header-icon"])}'
                f'!!{tunit("table-header-name", special_tunit_entries["table-header-name"])}'+
                (f'!!data-sort-type="number"|{tunit("table-header-warmth", special_tunit_entries["table-header-warmth"])}' if has_warmth != 0 else "")+
                (f'!!data-sort-type="number"|{tunit("table-header-rain-prot", special_tunit_entries["table-header-rain-prot"])}' if has_rain_prot != 0 else "")+
                (f'!!{tunit("table-header-eye-prot", special_tunit_entries["table-header-eye-prot"])}' if has_eye_prot != 0 else "")+
                (f'!!{tunit("table-header-desc", special_tunit_entries["table-header-desc"])}' if has_descriptions != 0 else "")+
                (f'!!{tunit("table-header-sold-to", special_tunit_entries["table-header-sold-to"])}' if has_bought_by != 0 else "")+
                (f'!!{tunit("table-header-bought-from", special_tunit_entries["table-header-bought-from"])}' if has_sold_by != 0 else "")+
                (f'!!{tunit("table-header-craftable", special_tunit_entries["table-header-craftable"])}' if has_craftable != 0 else "")+
                (f'!!{tunit("table-header-lootpool", special_tunit_entries["table-header-lootpool"])}' if has_lootable != 0 else "")+
                (f'!!{tunit("table-header-other-means", special_tunit_entries["table-header-other-means"])}' if has_other_means != 0 else "")+
                '\n'
                '|-\n'
             )
        for item in categories[category]:

            out+=(
                f"|[[File:{item}.png|64px]]"
                f"||{items[item].replace("_-XYZ-_", "" if not annot_bools["no_name"] else annot_bools["no_name"])}"+
                (f"||{f"{warmth[item]}" if item in warmth else ""}" if has_warmth else "")+
                (f"||{f"{rain_prot[item]}" if item in rain_prot else ""}" if has_rain_prot else "")+
                (f"||{f"{eye_prot[item]}" if item in eye_prot else ""}" if has_eye_prot else "")+
                (f"||{f"{descriptions[item]}" if item in descriptions else ""}" if has_descriptions else "")+
                (f"||{f"{",<br>".join(bought_by[item][0]).replace("_-XYZ-_", "" if not annot_bools["villager"] else annot_bools["villager"])}" if item in bought_by else ""}" if has_bought_by else "")+
                (f"||{f"{",<br>".join(sold_by[item][0]).replace("_-XYZ-_", "" if not annot_bools["villager"] else annot_bools["villager"])}" if item in sold_by else ""}" if has_sold_by else "")+
                (f"||{f"{craftable[item]}" if item in craftable else ""}" if has_craftable else "")+
                (f"||{f"{lootable[item]}" if item in lootable else ""}" if has_lootable else "")+
                (f"||{f"{other_means[item]}" if item in other_means else ""}" if has_other_means else "")+
                "\n|-\n"
            )

            if csv and category != "--all" and item in craftable:
                tmp=(
                    f"{items[item].replace("_-XYZ-_", "" if not annot_bools["no_name"] else annot_bools["no_name"])}"+
                    f",{special_tunit_entries["title-"+category]}"+
                    (f",{f"{warmth[item]}" if item in warmth else ""}" if has_warmth else "")+
                    (f",{f"{rain_prot[item]}" if item in rain_prot else ""}" if has_rain_prot else "")+
                    (f",{f"{",<br>".join(sold_by[item][0]).replace("_-XYZ-_", "" if not annot_bools["villager"] else annot_bools["villager"])}" if item in sold_by else ""}" if has_sold_by else "")+
                    (f",{f"{",<br>".join(bought_by[item][0]).replace("_-XYZ-_", "" if not annot_bools["villager"] else annot_bools["villager"])}" if item in bought_by else ""}" if has_bought_by else "")+
                    (f",{f"{craftable[item]}" if item in craftable else ""}" if has_craftable else "")+
                    "\n"
                ).replace("<translate>","").replace("</translate>","")
                csv+=tmp

        out+=""+\
            "|}"+\
            "<br>".join([f"<sup>{i+1}</sup>{annotations_inner[i]}" for i in range(len(annotations_inner))])+\
            "\n|}"

        if category != "--all":
            combined_tables.append(out)

        write_file(output_path+f"/generated/tables/{category}.txt", out, encode_json=False)


    combined_tables.append("<references/>")

    combined_tables_string = "\n".join(combined_tables)
    write_file(output_path+"/generated/tables/_combined.txt", combined_tables_string, encode_json=False)
    write_file_safe(output_path + "/re_input/table.txt", combined_tables_string, encode_json=False)
    write_file("./generated/clothes_3_combined_tables.txt", combined_tables_string, encode_json=False)

    trans_help=["<!--This is here for easier translation of the table using Tunit. Do not touch this if you don't know what you're doing!-->", "{{Hovertip||"]
    tunit_entries = [(entry, special_tunit_entries[entry]) for entry in special_tunit_entries] + [(trader, trader_util.translate_trader(install_path, trader, lang=lang)) for trader in trader_util.get_trader_ids()]
    trans_help += [f"<translate><!--T:{entry[0]}--> {entry[1]}</translate>" for entry in tunit_entries] + ["}}", trans_help[0]]
    trans_help = "<languages/>\n"+("\n".join(trans_help))
    write_file(output_path+"/generated/translation_help.txt", trans_help, encode_json=False)
    write_file("./generated/clothes_0_translation_help.txt", trans_help, encode_json=False)


    if csv:
        write_file("./generated/zestydippingsauce.csv", csv, encode_json=False)

