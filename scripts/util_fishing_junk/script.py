from scripts._util_general.file_util import read_file, write_file
from pathlib import Path
import json
from scripts._util_general.json_util import repair
from datetime import timedelta, datetime
start = datetime.now()

def generate(install_path:str, *, output_path:str="./", lang):
    global fishing_junk

    fishing_junk = read_file(install_path+"/assets/survival/entities/nonliving/bobber.json", decode_json=True)["attributes"]["junkCatches"]

    tmp=fishing_junk
    fishing_junk={fishing_junk[i]["code"]:fishing_junk[i]["weight"] for i in range(len(fishing_junk))}
    if len(fishing_junk)!=len(tmp):
        raise Exception("well fuck, we lost him")

    weight_sum=0
    for weight in fishing_junk.values():
        weight_sum+=weight
    for item in fishing_junk:
        fishing_junk[item]/=weight_sum

    write_file(output_path + "generated/weight_sum.txt", str(weight_sum), encode_json=False)
    write_file(output_path+"generated/fish.json", fishing_junk, encode_json=True)
    print(datetime.now()-start)


### destinction_fun expects a function to specify what kinda of items are wanted. It should be able to receive 1 string parameter e.g.:
###   `pannable_by_type(destinction_fun=(lambda item: item.startswith("clothes-")))` to narrow it down to just clothing items.
def fishable_by_type(destinction_fun):
    out={}
    return json.loads(json.dumps({item:fishing_junk[item] for item in fishing_junk if destinction_fun(item)}))