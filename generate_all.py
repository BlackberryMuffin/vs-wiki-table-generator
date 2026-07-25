from datetime import datetime, timedelta
start = datetime.now()
from sys import argv
from os import scandir, path as os_path
from importlib import import_module
from shutil import rmtree

def generate(install_path:str, *, lang:str="en", debug=True):
    print("Starting to set up utility scripts:")
    path_prefix = "scripts"
    directories = [(path_prefix, entry.name) for entry in scandir("scripts/") if entry.is_dir() and not entry.name.startswith((".", "_"))]
    directories.sort()
    directories = [entry for entry in directories if entry[1].startswith("util_")] +\
                  [entry for entry in directories if not entry[1].startswith("util_")]

    if os_path.exists("./generated/"):
        rmtree("./generated/")
    sub_times={}
    for entry in directories:
        sub_times[entry[1]]=datetime.now()
        generated_path = "/".join(entry) + "/generated"
        if os_path.exists(generated_path):
            rmtree(generated_path)
        import_module(".".join(entry)+".script").generate(install_path=install_path, output_path="/".join(entry)+"/", lang=lang)
        sub_times[entry[1]]=datetime.now()-sub_times[entry[1]]
        if debug:
            print(f"\tFinished setting up {entry[1]} in:".ljust(45) + f"{sub_times[entry[1]]}~{(round(sub_times[entry[1]] / timedelta(milliseconds=1)))} ms")

    print("All done :3")
    def sum_timedelta(l:list):
        out=timedelta(0)
        for td in l: out+=td;
        return out
    total_time = datetime.now() - start
    time_lost=total_time-sum_timedelta(sub_times.values())
    if time_lost/timedelta(milliseconds=1)<1:
        time_lost = int(time_lost/timedelta(microseconds=1))
    print("It took:", total_time)
    print(f"Lost {time_lost} μs to the eather >:3") # debug=True adds ~70μs to this



if len(argv)<2:
    print(f"Missing arguments. Should be '{argv[0]} <install_path> [<lang>]'")
elif len(argv) == 2:
    generate(install_path=argv[1])
else:
    generate(argv[1], lang=argv[2])
