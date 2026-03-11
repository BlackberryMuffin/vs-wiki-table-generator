import re

def repair(broken_json:str, *, correct_wildcards=True):
    out = broken_json
    out = re.sub("(\\w+):", r'"\1":', out)          # adds double quotes around keys which didn't have them
    out = re.sub("(\\s*,)+\\s*([]}])", "\\2", out)  # removes commas after the last element of arrays/dicts
    out = re.sub("\\s*//.*", "", out)               # removes `//` inline comments
    out = re.sub("'(([^']|\\\\')*[^\\\\])'", '"\\1"', out) # replaces '$1' strings with "$1"

    if correct_wildcards:
        out = out.replace("@.*", chr(2**20))
        out = out.replace("@*", chr(2**20))
        out = out.replace("*", chr(2**20))

        out = out.replace(chr(2**20), ".*")

    return out