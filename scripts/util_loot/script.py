import json
from scripts._util_general.file_util import read_file, write_file
from scripts.util_0lang.LangDict import LangDict
from scripts.util_0lang.script import get_dict

def generate(install_path:str, *, script_path:str, lang:str, debug:bool):
    global stackrandomizer
    lang_dict:LangDict = get_dict(lang=lang)

    stackrandomizer=read_file(install_path+"/assets/survival/itemtypes/meta/stackrandomizer.json", decode_json=True)
    for stack_type in stackrandomizer["variantgroups"][0]["states"]:
        if not ".*-"+stack_type in stackrandomizer["attributesByType"]:
            print("\t\tWARNING:", stack_type, "is not a used variant group")

    type_sum={}
    type_sum_new={}
    dupes=[]
    mw_tables=""
    ugh=set()
    for stack_type in stackrandomizer["attributesByType"]:
        if not stack_type[3:] in stackrandomizer["variantgroups"][0]["states"]:
            print("\t\tWARNING:", stack_type, "is not a marked variant group")
        type_sum[stack_type]=0
        type_sum_new[stack_type]=0
        items=stackrandomizer["attributesByType"][stack_type]["stacks"]
        i=0
        uniques={} # see clothes-arm-silver-chain as of 1.22-rc.2 to understand why this exists.
        while i < len(items):
            name=items[i]["type"]+items[i]["code"]+items[i]["code"]+\
                     str(items[i]["attributes"] if "attributes" in items[i] else "")+\
                     str(items[i]["quantity"] if "quantity" in items[i] else "")
            if name in uniques:
                items[uniques[name]]["chance"]+=items[i]["chance"]
                dupes.append(items.pop(i))
                i-=1
            else:
                uniques[name]=i
            type_sum[stack_type]+=items[i]["chance"]
            i+=1
        for item in items:
            item["chance"]=item["chance"]/type_sum[stack_type]
        for item in items:
            type_sum_new[stack_type]+=item["chance"]
        ### On one hand, this snippet (and the file write) shouldn't be in a utils folder,
        ### but on the other hand moving this to a dedicated file (with its own loop) just feels wasteful
        mw_tables += (
                f"<translate>=== {lang_dict[stack_type.replace('.*', 'item-stackrandomizer')]} ===</translate>\n"+
                "{| class=\"wikitable sortable mw-collapsible mw-collapsed\"||-\n" +
                f"|+{stack_type}||-\n" +
                "!<translate>Item</translate>!!<translate>Chance</translate>\n" +
                f"|- ||{'\n|-\n|'.join([
                    f'<translate>{
                        lang_dict.__getitem__(
                            f"{item['type']}-{item['code']}",
                            item["attributes"] if "attributes" in item else {}
                        )
                    }</translate>||{round(item["chance"]*100,2)}%'
                    for item in items
                ])}\n" +
                "|}\n\n"
        )

    write_file(script_path+"/generated/chance_sums_new.json", type_sum_new, encode_json=True)
    write_file(script_path+"/generated/chance_sums.json", type_sum, encode_json=True)
    write_file(script_path+"/generated/stackrandomizer.json", stackrandomizer, encode_json=True)
    write_file(script_path+"/generated/dupes.json", dupes, encode_json=True)
    write_file("generated/stackrandomizers.txt", mw_tables)


### destinction_fun expects a function to specify what kinda of items are wanted. It should be able to receive 1 string parameter e.g.:
###   `lootable_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))` to narrow it down to just clothing items.
def lootable_by_type(destinction_fun):
    out={}
    for stack_type in stackrandomizer["attributesByType"]:
        for item in stackrandomizer["attributesByType"][stack_type]["stacks"]:
            if destinction_fun(item["code"]):
                if item["code"] not in out:
                    out[item["code"]] = []
                out[item["code"]].append((stack_type, item["chance"]))
    return json.loads(json.dumps(out))


