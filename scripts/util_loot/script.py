import json
from scripts._util_general.file_util import read_file, write_file
from pathlib import Path

def generate(install_path:str, output_path:str, *, lang:str="en", gen_cleaned_jsons:bool=True):
    global stackrandomizer

    stackrandomizer=read_file(install_path+"/assets/survival/itemtypes/meta/stackrandomizer.json", decode_json=True)
    for stack_type in stackrandomizer["variantgroups"][0]["states"]:
        if not ".*-"+stack_type in stackrandomizer["attributesByType"]:
            print("\t\tWARNING:", stack_type, "is not a used variant group")

    type_sum={}
    type_sum_new={}
    dupes=[]
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

    write_file(output_path+"/generated/chance_sums_new.json", type_sum_new, encode_json=True)
    write_file(output_path+"/generated/chance_sums.json", type_sum, encode_json=True)
    write_file(output_path+"/generated/stackrandomizer.json", stackrandomizer, encode_json=True)
    write_file(output_path+"/generated/dupes.json", dupes, encode_json=True)


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


