def generate(install_path:str):
    from os import scandir, path as os_path
    from importlib import import_module
    from shutil import rmtree
    print("Starting to set up utility scripts:")
    with scandir() as it:
        for entry in it:
            generated_path = entry.name+"/generated"
            if entry.name.startswith("util_") and entry.is_dir():
                if os_path.exists(generated_path):
                    rmtree(generated_path)
                import_module(entry.name+".script").generate_tables(install_path=install_path, output_path=entry.name+"/")
                print("\tFinished setting up "+entry.name)
    print("All utility scripts are set up. Launching generational scripts")
    with scandir() as it:
        for entry in it:
            generated_path = entry.name+"/generated"
            if not entry.name.startswith((".","_","util_")) and entry.is_dir():
                if os_path.exists(generated_path):
                    rmtree(generated_path)
                import_module(entry.name+".script").generate_tables(install_path=install_path, output_path=entry.name+"/")
                print("\tFinished genertating "+entry.name)
    print("All done :3")

generate("/home/philip/.config/VSLGameVersions/1.22.0-pre.5/") ### My debug thing that I'm too lazy to filter out of the git
