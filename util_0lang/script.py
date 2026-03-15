import json
from pathlib import Path

dicts={}
get_dict=set_dict=None

def generate(install_path:str, *, output_path:str="./", lang:str="en"):
    global get_dict, set_dict
    Path(output_path + "/generated/").mkdir(parents=True, exist_ok=True)
    def get_dict(lang:str="en", *, fix_missing=True):
        set_dict(lang)
        return dicts[lang+("_fixed" if fix_missing else "")]

    def set_dict(lang:str):
        if lang in dicts:
            return
        with open(f"{install_path}/assets/game/lang/{lang}.json", "r") as f:
            dicts[lang] = json.load(f)
        dicts[lang+"_fixed"] = {w: ( dicts[lang] if w in dicts[lang] else dicts["en"] )[w] for w in dicts["en"]}
        dicts[lang+"_missing"] = [w for w in dicts["en"] if w not in dicts[lang]]

        #if dicts[lang+"_missing"]: print("\n\t>\t"+("\n\t>\t".join(dicts[lang+"_missing"])))
        with open(output_path+f"/generated/{lang}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(dicts[lang], indent=4))

    set_dict("en")
    set_dict(lang)