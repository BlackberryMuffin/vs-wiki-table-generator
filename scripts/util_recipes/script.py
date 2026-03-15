from scripts._util_general.file_util import read_file, write_file
from datetime import timedelta, datetime
start = datetime.now()
from os import scandir
from scripts._util_general.json_util import repair as repair_json
from pathlib import Path
import json

"""
A lot of the grid recipes have horizontal tabulators inside strings, which is not allowed under standard JSON.
To search for relevant shapes look for
    ".*	.*"
    (starting and ending with the quotation marks))
within the vanilla (not generated) grid recipes. Idk if this will cause problems yet.
"""
r"""
Oh gods no, there are some recipes with multiple wildcards, look for in the generated recipes:
    "([^"\n]*\{[^"\n}]*})([^"\n]*\{[^"\n}]*})+[^"\n]*"
    (starting and ending with the quotation marks))
"""

def generate(install_path:str, output_path:str, *, lang:str="en", gen_cleaned_jsons:bool=True):
    global recipes
    recipes={}

    sub_dirs=[(install_path+"/assets/survival/recipes/grid/", "")]
    i=0
    while i < len(sub_dirs):
        with scandir(sub_dirs[i][0]) as dirs:
            for entry in dirs:
                if entry.is_dir():
                    sub_dirs.append((entry.path, sub_dirs[i][1]+entry.name+"-"))
                elif entry.is_file() and entry.name.endswith(".json"):
                    file_path=sub_dirs[i][1]+entry.name[:-5]
                    recipes[file_path] = read_file(entry.path, decode_json=True)
                    if gen_cleaned_jsons:
                        path = output_path + "/generated/cleaned_jsons/" + "/".join(sub_dirs[i][1].split("-"))
                        write_file(path+entry.name, recipes[file_path], encode_json=True)
        i+=1
    if gen_cleaned_jsons:
        write_file(output_path+"/generated/cleaned_jsons/_combined.json", recipes, encode_json=True)
    print(datetime.now()-start)



### destinction_fun expects a function to specify what kinda of items are wanted. It should be able to receive 1 string parameter e.g.:
###   `recipes_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))` to narrow it down to just clothing items.
def recipes_by_type(destinction_fun):
    out={}
    for recipe_category in recipes:
        if destinction_fun(recipe_category):
            for recipe in recipes[recipe_category]:
                if recipe["output"]["code"] not in out:
                    out[recipe["output"]["code"]] = []
                out[recipe["output"]["code"]].append(recipe)
    return json.loads(json.dumps(out))
























