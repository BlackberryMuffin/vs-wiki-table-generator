from scripts._util_general.data_util import deep_copy
from scripts._util_general.file_util import read_file, write_file
from os import scandir, path as os_path
from numpy import array
import re
from scripts.util_recipes.script import recipes_by_type
from json import dumps

def get_test_var():
    return test_var

def gen_clothing_attributes(install_path:str, output_path:str, debug:bool):
    global clothing_attributes
    if "clothing_attributes" in globals():
        return

    clothing_attributes={}

    sub_dirs=[(install_path+"/assets/survival/itemtypes/wearable/seraph/", "")]
    i=0
    while i < len(sub_dirs):
        with scandir(sub_dirs[i][0]) as dirs:
            for entry in dirs:
                if entry.is_dir():
                    sub_dirs.append((entry.path, sub_dirs[i][1]+((entry.name+"-") if entry.name != "villager" else "")))
                elif entry.is_file() and entry.name.endswith(".json"):
                    clothing_attributes[sub_dirs[i][1]+entry.name[:-5]] = read_file(entry.path, decode_json=True)
                    if debug:
                        path=output_path + "/generated/cleaned_jsons/"+"/".join(sub_dirs[i][1].split("-"))
                        write_file(path+entry.name, clothing_attributes[sub_dirs[i][1]+entry.name[:-5]], encode_json=True)
        i+=1
    if debug:
        write_file(output_path + "/generated/cleaned_jsons/_combined.json", clothing_attributes, encode_json=True)


def get_attributes(item:str, debug):
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

def shape(l:list):
    out=None
    try:
        out = array(l).shape
    except:
        pass
    if not out or 0 in out:
        print("Misshapen list", l)
    else:
        return out

def crafting_help(install_path:str, output_path:str, lang_dict):
    specials = {
        "color": [w[11:] for w in lang_dict if w.startswith("item-cloth-")]
    }

    ### Generate the main dictionary from JSON data
    recipes = recipes_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))

    ### Remove malformed elements that don't state an ingredient patter
    ### Add a more usable pattern in the form of a 2D array
    lessers = []
    for item_id, item_recipes in recipes.items():
        for i, item_recipe in enumerate(item_recipes):
            if "ingredientPattern" not in item_recipe:
                print(f"\t\tRecipe #{i} of item {item_id} has no ingredient pattern; Skipping!")
                lessers.append((item_id, i))
                continue
            item_recipe["patternAs2DList"] = [list(e) for e in item_recipe["ingredientPattern"].strip(",").split(",")]
            if len((arr:=item_recipe["patternAs2DList"])[0])>3:
                if len(arr)>1 or len(arr[0])%3!=0 or len(arr[0])>9:
                    print(f"\t\tRecipe #{i} of item {item_id} is fucked beyond saving; Retroactively removing!")
                    lessers.append((item_id, i))
                    continue
                item_recipe["patternAs2DList"] = [arr[0][i:i + 3] for i in range(0, len(arr[0]), 3)]
            # for ing in e["ingredients"].values():
            #     for sub_key, sub in ing.items():
            #         if sub_key!="returnedStack" and type(sub) not in (int, bool, str) and len(sub) > 1:
            #             print(k, i, sub_key, ing)
            #             break
    for k, i in lessers:
        del recipes[k][i]

    ### Removes wild cards from recipes, e.g.: clothes-arm-{seed} -> clothes-arm-bamboo, clothes-arm-cattail, ...
    replace = {}
    for clothing in recipes: ### We go through all recipes, `clothing` is the key
        s = re.search(r"(\{.*})", clothing)
        if s: ### If they key string contains a wild-card (a part surrounded by {}), e.g. clothes-arm-{seed}:
            replace[clothing] = {}  ### Initialize the key string for the replace dict
            clothing_copy = clothing    ### copy the key string into a new variable
            while s:
                wild_card = s[0][1:-1]  ### Store the (first) wild-card in a variable
                new = None  ### initialize `new`
                for sub_recipe in recipes[clothing]:    ### loop through the list of recipes per recipe
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
    write_file(output_path + "/generated/recipes/wild_cards.json", [clothing for clothing in replace], encode_json=True)

    ### DEBUG addition, just tests the warning system
    for clothing in replace:
        if re.search(r"(.*\{[^}]*})(.*\{[^}]*})+.*", clothing):
            print("\t\tPANIC: THERE IS A CLOTHING RECIPE WITH MORE THAN ONE WILD CARD!!! IT IS:\t", clothing)
            continue
        for replacee in replace[clothing]:
            for replacement in replace[clothing][replacee]:
                name = clothing.replace(replacee, replacement)
                recipes[name] = deep_copy(recipes[clothing])
                for sub_recipe in recipes[name]:
                    for ingredient in sub_recipe["ingredients"]:
                        if "code" in sub_recipe["ingredients"][ingredient] and replacee in \
                                sub_recipe["ingredients"][ingredient]["code"]:
                            tmp = sub_recipe["ingredients"][ingredient]
                            tmp["code"] = tmp["code"].replace(replacee, replacement)
        del recipes[clothing]
    write_file(output_path + "/generated/recipes/main.json", recipes, encode_json=True)

    multi = []
    fakes = []
    for recipe in recipes:
        if not recipe.startswith("clothes-"):
            fakes.append(recipe)
        elif len(recipes[recipe]) > 1:
            multi.append(recipe)
    write_file(output_path + "/generated/recipes/fake.json", fakes, encode_json=True)
    write_file(output_path + "/generated/recipes/multi.json", multi, encode_json=True)

    columns = ("A", "B", "C")
    rows = ("1", "2", "3")
    chars = []
    ### Add Template:Grid/Crafting strings using the previously added patternAs2DList
    for item, sub_recipes in recipes.items():
        for recipe in sub_recipes:
            pattern = recipe["patternAs2DList"]
            #if item=="clothes-upperbodyover-arcticfisher" or item=="clothes-upperbodyover-embroideredfur": print(item, pattern, "\n"+"\n".join([str(l) for l in pattern]), "\n"*3)
            if not shape(pattern):
                continue
            grid = ["{{Grid/Crafting"]
            for i, l in enumerate(pattern):
                for j, v in enumerate(l):
                    if v not in chars:
                        chars.append(v)
                    if v == "_":
                        continue
                    cell = columns[i] + rows[j]
                    grid.append(
                        f"|{cell}=None"+\
                        f"|{cell}-image={item}.png" ## TODO `item` must be replaced with the appropriate ingredient
                    )
            grid.append("}}")

    chars.sort()
    print(f"\t\tUsed characters for recipe patterns: '{"".join(chars)}'")











    return {recipe:recipes[recipe] for recipe in recipes if recipe not in fakes}


### It's a bit flawed, as it always assumes the first t_id to be the items name, then the second its description
def get_old_t_ids(input_path:str):
    file_name=input_path+"/table.txt"
    if not os_path.exists(file_name):
        return {}
    contents = read_file(file_name, decode_json=False).split("|-")
    out={}

    for content in contents:
        name=re.findall(r"\[\[File\:(.+)\.png\|64px\]\]", content)
        t_ids=re.findall(r"\<\!\-\-T\:\d+\-\-\> ", content)
        if re.search(r"\[\[File:([\w+]+).png|\d\dpx]]", content) and t_ids:
            if len(name) > 1 or len(t_ids) > 2:
                print("WARNING: TOO MUCH STUFF, YOU FAILED")
            out[name[0]] = {
                "name": t_ids[0],
                "desc": t_ids[1] if len(t_ids) > 1 else "",
            }
    return out