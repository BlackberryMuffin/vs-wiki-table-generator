import json
from pathlib import Path

dicts={}

def get_dict(install_path:str, lang:str="en", *, fix_missing=True):
    if not "en" in dicts:
        set_dict(install_path)
    set_dict(install_path, lang)

    if not fix_missing:
        return dicts[lang]
    return {w:(dicts[lang] if w in dicts[lang] else dicts["en"])[w] for w in dicts["en"]}

def set_dict(install_path:str, lang:str="en"):
    if lang in dicts:
        return
    with open(f"{install_path}/assets/game/lang/{lang}.json", "r") as f:
        dicts[lang] = json.load(f)
    Path("_util_general/generated/lang/").mkdir(parents=True, exist_ok=True)
    with open(f"_util_general/generated/lang/{lang}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(dicts[lang], indent=4))