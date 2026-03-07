def generate(install_path:str):
    from os import scandir
    from importlib import import_module
    print("Starting to set up utility scripts:")
    with scandir() as it:
        for entry in it:
            if entry.name.startswith("util_") and entry.is_dir():
                import_module(entry.name+".script").generate_tables(install_path=install_path, output_path=entry.name+"/")
                print("\tFinished setting up "+entry.name)
    print("All utility scripts are set up. Launching generational scripts")
    with scandir() as it:
        for entry in it:
            if not entry.name.startswith((".","_","util_")) and entry.is_dir():
                import_module(entry.name+".script").generate_tables(install_path=install_path, output_path=entry.name+"/")
                print("\tFinished genertating "+entry.name)
    print("All done :3")
generate("/home/philip/.config/VSLGameVersions/1.22.0-pre.5/")
