from sys import argv
from os import scandir, path as os_path
from importlib import import_module
from shutil import rmtree

def generate(install_path:str, *, lang:str="en"):
    print("Starting to set up utility scripts:")
    with scandir() as it:
        for entry in it:
            generated_path = entry.name+"/generated"
            if entry.name.startswith("util_") and entry.is_dir():
                if os_path.exists(generated_path):
                    rmtree(generated_path)
                import_module(entry.name+".script").setup(install_path=install_path, output_path=entry.name+"/", lang=lang)
                print("\tFinished setting up "+entry.name)
    print("All utility scripts are set up. Launching generational scripts")
    with scandir() as it:
        for entry in it:
            generated_path = entry.name+"/generated"
            if not entry.name.startswith((".","_","util_")) and entry.is_dir():
                if os_path.exists(generated_path):
                    rmtree(generated_path)
                import_module(entry.name+".script").generate(install_path=install_path, output_path=entry.name+"/", lang=lang)
                print("\tFinished genertating "+entry.name)
    print("All done :3")

if len(argv)>1:
    if len(argv) == 2:
        generate(install_path=argv[1])
    else:
        generate(argv[1], lang=argv[2])
