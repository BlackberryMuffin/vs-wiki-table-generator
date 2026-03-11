import json
from pathlib import Path

dicts={}

def get_dict(install_path:str, lang:str="en"):
    if not lang in dicts:
        with open(f"{install_path}/assets/game/lang/{lang}.json", "r") as f:
            dicts[lang] = json.load(f)
        Path("_util_general/generated/lang/").mkdir(parents=True, exist_ok=True)
        with open(f"_util_general/generated/lang/{lang}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(dicts[lang], indent=4))

    return dicts[lang]