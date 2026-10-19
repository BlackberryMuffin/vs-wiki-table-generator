from pathlib import Path
from os import listdir as ls
from scripts.util_0lang.script import get_dict


def generate(install_path:str, *, script_path:str, lang:str, debug:bool):
    lang_dict = get_dict(lang)
    path_out = script_path+"/generated/"
    path_out_blocks, path_out_items = path_out+"/blocks/", path_out+"/items/"



    def write_file(file_name:str, file_content:str):
        file_path = Path(file_name)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
        elif not file_path.parent.is_dir():
            raise Exception(f"Path {file_path.parent} is must be a directory, but is not.")
        open(file_name, "w", encoding="utf-8").write(file_content)

    paths = {
        "blockcodes": (script_path+"/input/block_codes.txt", "block codes list"),
        "itemcodes": (script_path+"/input/item_codes.txt", "item code list"),
        "blockpage": (script_path+"/re_input/block_page.txt", "old blocks-table"),
        "itempage": (script_path+"/re_input/item_page.txt", "old items-table"),
    }

    file_contents = {key:
                         (
                             path,
                             (open(path).read() if Path(path).exists() else ""),
                             name
                         )
                     for key, (path, name) in paths.items()
                    }
    data = {}
    missing = False
    for key, (path, content, name) in file_contents.items():
        if not content:
            write_file(path, "")
            print(f"The '{name}' is missing. Please paste it into '{path}' and try again.")
            missing += True
        if key in ("blockcodes", "itemcodes"):
            # [Code]
            data[key] = [code.strip() for code in content.split("\n") if code.strip()]
        else:
            # [Item, Code, Creative Tab, Notes]
            tmp = [[cell.strip() for cell in line.split("||")] for line in content.split("|}")[0].split("|-")[1:] if line.strip()]
            data[key] = {code: (item, code, c_tab, notes) for (item, code, c_tab, notes) in tmp}
            if mishaps := [e for e in data[key].values() if len(e)!=4]:
                raise Exception(f"There are weirdnesses in the '{name}':\n\t{'\n\t'.join([str(e) for e in mishaps])}")
    if missing:
        print(f"Since the contents of {missing} file{'s' * missing!=1} were missing, Block/Item code page generation will be skipped")
        return

    lost_item_ids = [item for (_, item, _, _) in data["itempage"].values() if item not in data["itemcodes"]]
    lost_block_ids = [block for (_, block, _, _) in data["blockpage"].values() if block not in data["blockcodes"]]
    tmp_file_name_item, tmp_file_name_block = path_out_items+"lost_item_ids.txt", path_out_items+"lost_block_ids.txt"

    write_file(tmp_file_name_item, "\n".join(lost_item_ids))
    if debug and lost_item_ids:
        print(f"Some item codes seem to no longer exist. You can find them in '{tmp_file_name_item}'")
    write_file(tmp_file_name_block, "\n".join(lost_block_ids))
    if debug and lost_block_ids:
        print(f"Some block codes seem to no longer exist. You can find them in '{tmp_file_name_block}'")


    if debug:
        from sys import setrecursionlimit, _getframe
        setrecursionlimit(20)
        _=[lang_dict[id] for id in (
                [f'block-{block}' for block in data["blockcodes"]]+
                [f'item-{item}' for item in data["itemcodes"]]
        )]
        if lang_dict.lang_codeErrorCounter:
            errors = sorted([(len(v), k, v) for k,v in lang_dict.error_codes.items()], reverse=True)
            print(
                f"\tThere's {lang_dict.lang_codeErrorCounter} bad keys, with the top primaries are:\n\t\t"+
                "\n\t\t".join((str(t[:2]) for t in errors[:5]))+"\n"+
                f'Find out more near File "{__file__}", line {_getframe().f_lineno}'
            )
        setrecursionlimit(1000); del setrecursionlimit, _getframe

