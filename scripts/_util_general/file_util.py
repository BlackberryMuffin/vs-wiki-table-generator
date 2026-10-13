from os import rename
from pathlib import Path
import json

from scripts._util_general.json_util import repair


def write_file_safe(file_name:str, content, encode_json:bool=False):
    write_file(file_name+".failsafe_measure", content, encode_json=encode_json)
    rename(file_name+".failsafe_measure", file_name)

def read_file(file_name:str, decode_json:bool=False):
    if not Path(file_name).exists():
        return ""
    content = open(file_name, "r", encoding="utf-8").read()
    return json.loads(repair(content)) if decode_json else content

def write_file(file_name:str, content, encode_json:bool=False):
    file_path = Path(file_name)
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    elif not file_path.is_dir():
        raise Exception(f"Path {file_path.parent} is must be a directory, but is not.")
    open(file_name, "w", encoding="utf-8").write(json.dumps(content, indent=4) if encode_json else content)