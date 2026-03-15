from os import rename, path, remove
from pathlib import Path
import json

from scripts._util_general.json_util import repair


def write_file_safe(file_name:str, content, encode_json:bool):
    write_file(file_name+".failsafe_measure", content, encode_json=encode_json)
    rename(file_name+".failsafe_measure", file_name)

def read_file(file_name:str, decode_json:bool):
    if not path.exists(file_name):
        return ""
    content = open(file_name, "r", encoding="utf-8").read()
    return json.loads(repair(content)) if decode_json else content

def write_file(file_name:str, content, encode_json:bool):
    exists = path.exists(file_name)
    if not exists and not path.exists(path.dirname(file_name)):
        Path(path.dirname(file_name)).mkdir(parents=True, exist_ok=True)
    _help_write_file(file_name, "w" if exists else "x", content, encode_json)


def _help_write_file(file_name:str, open_type:str, content:str, encode_json):
    with open(file_name, open_type, encoding="utf-8") as file:
        file.write(json.dumps(content, indent=4) if encode_json else content)
