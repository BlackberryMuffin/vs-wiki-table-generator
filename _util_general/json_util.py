import re

def repair(broken_json:str, *, correct_wildcards=True):
    out = broken_json
    out = re.sub(r"(\w+):", r'"\1":', out)          # adds double quotes around keys which didn't have them
    out = re.sub(r"(\s*,)+\s*([]}])", r"\2", out)   # removes commas after the last element of arrays/dicts
    out = re.sub(r"\s*//.*", r"", out)               # removes `//`-style inline comments
    out = re.sub(r"'(([^'\n]|\\')*[^\\\n])?'", r'"\1"', out) # replaces '$1' strings with "$1"

    # Removes horizontal tabulators from within strings
    """# Right now it's a bit more aggressive than necessary, since the inside of a string and the inbetween space of
    # two strings is indistinguishable.
    rem_tabs=lambda s: re.sub(r'"(([^"\n]|\\")*)?\t(([^"\n]|\\")*[^\\\n])?"',r'"\1 \3"', s)
    tmp=rem_tabs(out)
    while tmp != out:
        out = tmp
        tmp = rem_tabs(out)"""
    # why did I even bother?
    out = out.replace("\t", " ")

    if correct_wildcards:
        out = out.replace("@.*", chr(2**20))
        out = out.replace("@*", chr(2**20))
        out = out.replace("*", chr(2**20))

        out = out.replace(chr(2**20), ".*")

    return out