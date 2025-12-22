import requests
import defs
from backend import *
from args_parser import *
import re


add_flag("-s") # Search
add_flag("-g") # Get version id
add_flag("-f") # Find dependencies
add_flag("-d") # Download
add_flag("-o", 1) # output file, defaults to "mods.txt"
add_flag("-c", 1) # amount of search hits to show
add_flag("-v", 1) # minecraft version
add_flag("-l", 1) # minecraft loader

ofilename = "mods.txt"
ifilename = ""
top_c = 5 # amount of hits to show, defaults to 5
mc_loader = None
m_version = "1.21.11" # minecraft version to search for, defaults to newest, as of 17.12.2025 it's 1.21.11

args = parse_args()

# Set variables based on provided flags (its so fucking ugly :sob: )

if(len(args["_"]) > 0):
    ifilename = args["_"][0]
if("-o" in args):
    ofilename = args["-o"][0] if args["-o"][0] != "." else None
if("-c" in args):
    if(args["-c"][0] == None):
        top_c = 5
    else:
        top_c = int(args["-c"][0]) if args["-c"][0].isnumeric() else 5

if("-v" in args):
    if(args["-v"][0] != None):
        m_version = args["-v"][0]

if("-l" in args):
    if(args["-l"][0] != None):
        mc_loader = args["-l"][0]

# What actions to do

search = "-s" in args.keys()
get_version = "-g" in args.keys()
find_dependecies = "-f" in args.keys()
download = "-d" in args.keys()

find_dependecies = find_dependecies or (search and download)

if(not (search or find_dependecies or download)):
    print("No action specified!")
    print("use -h to see actions\n")
    exit()

# Validate some provided data

known_loaders = ["fabric", "forge", "quilt", "neoforge"]

if(mc_loader not in known_loaders):
    print(f"Unknown mod loader {mc_loader}")
    print("Do you wish to continue? y/N")
    choice = input("> ")
    if(len(choice) > 0 and choice[0].lower() == "y"):
        pass
    else:
        exit()
    print("")

# Checks if Minecraft version matches regex
# Either X.X.X or X.X (X can be any number)
# If version is set to * (any version) this check is skipped
if(re.fullmatch(r"[0-9]+\.[0-9]+(\.[0-9]+)?", m_version) == None and m_version != "*"):
    print(f"Invalid? Minecraft version {m_version}")
    print("Do you wish to continue? y/N")
    choice = input("> ")
    if(len(choice) > 0 and choice[0].lower() == "y"):
        pass
    else:
        exit()
    print("")




operating_data = []

def load_data():
    try:
        f = open(ifilename, "r")
    except FileNotFoundError:
        print(f"Could not open file {ifilename}")
        exit(1)
    for line in f.readlines():
        if("::" in line):
            operating_data.append(line.strip("\n\r").split("::", 1))
        else:
            operating_data.append(line.strip("\n\r"))

def search_multiple(queries: list):
    selected_mods = []
    for q in queries:
        hits = search_mod(q, top_c, m_version, mc_loader)
        if(hits == None):
            continue
        if(top_c == 1):
            selected_mods.append(hits[0]["project_id"])
            continue


        hit_number = 1
        digit_c = len(str(abs(len(hits))))
        for h in hits:
            print(f"{str(hit_number).rjust(digit_c)} - {h["title"]}")
            hit_number += 1
        selected = input("> ")
        print("")
        if(selected.lower() == "x"):
            print("Action aborted by user")
            exit()
        if(selected.isdigit() and int(selected) > 0 and int(selected) <= len(hits)):
            selected_mods.append(hits[int(selected) - 1]["project_id"])
    return selected_mods








def do_search_action():
    global operating_data
    if(mc_loader == None):
        print("Mod loader not specified!")
        exit(2)
    operating_data = search_multiple(operating_data)

def do_get_version_action():
    global operating_data

    pass


def do_find_dependencies_action():
    global operating_data
    print(get_dependencies(operating_data[0]))
    exit()




if(ifilename == ""):
    print("No input file")
    exit(1)

of = None
def out_text(t):
    if(of == None):
        print(t, end="")
    else:
        of.write(t)










def output():
    global of
    if(ofilename != None):
        try:
            of = open(ofilename, "w")
        except: 
            print(f"Could not open file {ofilename}")
            exit(1)
    for l in operating_data:
        if(type(l) == list and len(l) >= 2):
            out_text(f"{l[0]}::{l[1]}\n")
        else:
            out_text(f"{l}\n")




if __name__ == "__main__":
    load_data()
    print(ofilename)
    if(search):
        do_search_action()
    if(find_dependecies):
        do_find_dependencies_action()
    output()    