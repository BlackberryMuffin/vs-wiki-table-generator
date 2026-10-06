from sys import argv
from os import scandir, path as os_path
from importlib import import_module
from shutil import rmtree
from datetime import datetime, timedelta
start = datetime.now()


args_options = {
    ("--help", "-h"): (
        (),
        "Displays this help message. This option can be run with others, but will cancel all of them and print this info instead."
    ),
    ("--path", "-p"): (
        (
            "installDir",
        ),
        "The path to the relevant Vintage Story directory containing the 'assets/' folder.",
        "install_path",
    ),
    ("--lang", "-l"): (
        (
            "language",
        ),
        "The language to be used for table contents (defaults to 'en').",
        "lang",
    ),
    ("--plainTextHTML", "--plain"): (
        (),
        "Makes html tags display as plain text in an html viewer (this is for translation purposes).",
        "plainTextHTML",
    ),
    ("--debug", "-d"): (
        (),
        "Enables certain debug data being printed (mainly process times).",
        "debug",
    ),
}
args_options_simple = {k:v for keys,v in args_options.items() for k in keys}

def help_message(call_name):
    return (
        f"Usage: python {call_name} installDir [options...] |\n"+
        f"       python {call_name} [options...]\n"+
        "options:\n  "+
        "\n  ".join([f"{', '.join(key)}  {' '.join([f'<{arg}>' for arg in var[0]])} ".ljust(32)+var[1] for key, var in args_options.items()])
    )

def generate(args:list):
    values = {}
    if len(args) == 1: args.append("-h")
    args_iter = iter(args[1:])
    if args[1] not in args_options_simple:
        values["install_path"] = [next(args_iter)]

    for i, arg in enumerate(args_iter):
        if arg not in args_options_simple:
            raise Exception(f"Unknown option: '{arg}'\n\n{help_message(args[0])}")
        if args_options_simple[arg] == args_options_simple ["-h"]:
            print(help_message(args[0]))
            exit()
        title = args_options_simple[arg][2] if len(args_options_simple[arg])>=3 else arg
        if title in values:
            raise Exception(f"Option '{arg}' is present multiple times.")
        values[title] = [next(args_iter) for _ in args_options_simple[arg][0]]

    if "install_path" not in values:
        raise Exception(f"Missing required value: 'installDir'\n\n{help_message(args[0])}")

    install_path:str = values["install_path"][0]
    lang:str = values["lang"][0] if "lang" in values else "en"
    plainTextHTML:bool = True if "plainTextHTML" in values else False
    debug:bool = True if "debug" in values else False



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
        import_module(".".join(entry)+".script").generate(install_path=install_path, output_path="/".join(entry)+"/", lang=lang, debug=debug)
        sub_times[entry[1]]=datetime.now()-sub_times[entry[1]]
        if debug:
            print(f"\tFinished setting up {entry[1]} in:".ljust(45) + f"{sub_times[entry[1]]}, ~{(round(sub_times[entry[1]] / timedelta(milliseconds=1)))} ms")

    print("All done :3")
    def sum_timedelta(l:list):
        out=timedelta(0)
        for td in l: out+=td;
        return out
    total_time = datetime.now() - start
    time_lost=total_time-sum_timedelta(sub_times.values())
    if time_lost/timedelta(milliseconds=1)<1:
        time_lost = int(time_lost/timedelta(microseconds=1))
    if debug:
        print("It took:", total_time)
        print(f"Lost {time_lost} μs to the aether >:3") # debug=True adds ~70μs to this


generate(argv)