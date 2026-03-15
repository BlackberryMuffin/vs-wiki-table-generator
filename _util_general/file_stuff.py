from os import rename, path, remove
from pathlib import Path


def safe_write(file_name:str, content:str):
    if path.exists(file_name+".failsafe_measure"):
        remove(file_name+".failsafe_measure")
    elif not path.exists(path.dirname(file_name)):
        Path(path.dirname(file_name)).mkdir()
    with open(file_name+".failsafe_measure", "x", encoding="utf-8") as file:
        file.write(content)
    rename(file_name+".failsafe_measure", file_name)



simple_path=lambda s: "/".join([c for c in s.split("/") if c!=""])