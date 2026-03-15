import json

from scripts._util_general.file_util import read_file, write_file
from pathlib import Path

from scripts._util_general.json_util import repair

dicts={}
get_dict=set_dict=None

def generate(install_path:str, *, output_path:str="./", lang:str="en"):
    global get_dict, set_dict
    def get_dict(lang:str="en", *, fix_missing=True):
        set_dict(lang)
        return dicts[lang+("_fixed" if fix_missing else "")]

    def set_dict(lang:str):
        if lang in dicts:
            return

        ### This is relying on at least the lang files being properly JSON formatted.
        ### They are just too complex for my dinky li'l repair script
        dicts[lang] = json.loads(read_file(f"{install_path}/assets/game/lang/{lang}.json", decode_json=False))

        dicts[lang+"_fixed"] = {w: ( dicts[lang] if w in dicts[lang] else dicts["en"] )[w] for w in dicts["en"]}
        dicts[lang+"_missing"] = [w for w in dicts["en"] if w not in dicts[lang]]

        #if dicts[lang+"_missing"]: print("\n\t>\t"+("\n\t>\t".join(dicts[lang+"_missing"])))
        write_file(output_path+f"/generated/{lang}.json", dicts[lang], encode_json=True)

    set_dict("en")
    set_dict(lang)