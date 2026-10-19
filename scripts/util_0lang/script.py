from json import loads
from scripts._util_general.file_util import read_file, write_file
from scripts.util_0lang.LangDict import LangDict
from typing import cast

dicts={}
def get_dict(lang:str, *, fix_missing=True)->LangDict: pass
def _gen_dict(lang:str)->None: pass

def generate(install_path:str, *, script_path:str, lang:str, debug:bool):
    global get_dict, _gen_dict
   # noinspection PyShadowingNames
    def inner_get_dict(lang:str):
        _gen_dict(lang)
        return dicts[lang]
    # noinspection PyShadowingNames
    def inner_gen_dict(lang:str):
        if lang in dicts:
            return

        ### This is relying on at least the lang files being properly JSON formatted.
        ### They are just too complex for my dinky li'l repair script
        dicts[lang] = loads(read_file(f"{install_path}/assets/game/lang/{lang}.json"))

        if dicts[lang].keys()!=dicts["en"].keys():
            dicts[lang] = {key: (dicts[lang] if key in dicts[lang] else dicts["en"])[key] for key in dicts["en"]}
            dicts[lang+"_missing"] = [key for key in dicts["en"] if key not in dicts[lang]]
        dicts[lang] = LangDict(dicts[lang])

        write_file(script_path+f"/generated/{lang}.json", dicts[lang], encode_json=True)
    get_dict = inner_get_dict
    _gen_dict = inner_gen_dict

    _gen_dict("en")
    _gen_dict(lang)