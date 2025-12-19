import requests
import defs
from backend import *
from args_parser import *
add_flag("-s") # Search
add_flag("-f") # Find dependencies
add_flag("-d") # Download
add_flag("-o", 1) # output file, defaults to "mods.txt"
ofilename = "mods.txt"
ifilename = ""

args = parse_args()
if(len(args["_"]) > 0):
    ifilename = args["_"][0]
if("-o" in args):
    ofilename = args["-o"][0] if args["-o"][0] != "." else None



search = "-s" in args.keys()
find_dependecies = "-f" in args.keys()
download = "-d" in args.keys()

find_dependecies = find_dependecies or (search and download)

if(not (search or find_dependecies or download)):
    print("No action specified!")
    print("use -h to see actions\n")
    exit()


m_version = "1.21.11" # minecraft version to search for, defaults to newest, as of 17.12.2025 it's 1.21.11
top_c = 5 # amount of hits to show, defaults to 5
input_file_type = 0 # 0 for mod name list, 1 for id list
operating_data = []
def load_data():
    if(search):
        try:
            f = open(ifilename, "r")
        except FileNotFoundError:
            print(f"Could not open file {ifilename}")
            exit(1)
        for line in f.readlines():
            operating_data.append(line.lstrip("\n").lstrip("\r"))
    elif(find_dependecies):
        try:
            f = open(ifilename, "r")
        except FileNotFoundError:
            print(f"Could not open file {ifilename}")
            exit(1)
        for line in f.readlines():
            operating_data.append(line.lstrip("\n").lstrip("\r"))
    elif(download):
        try:
            f = open(ifilename, "r")
        except FileNotFoundError:
            print(f"Could not open file {ifilename}")
            exit(1)
        for line in f.readlines():
            operating_data.append(line.lstrip("\n").lstrip("\r").split("::", 1))






def do_search_action():
    global operating_data
    operating_data = search_multiple(operating_data)






if(ifilename == ""):
    print("No input file")
    exit(1)










def search_multiple(queries: list):
    selected_mods = []
    for q in queries:
        hits = search_mod(q, top_c, m_version)
        if(hits == None):
            continue
        hit_number = 1
        digit_c = len(str(abs(len(hits))))
        for h in hits:
            print(f"{str(hit_number).rjust(digit_c)} - {h["title"]}")
            hit_number += 1
        selected = input("> ")
        print("")
        if(selected.isdigit() and int(selected) > 0 and int(selected) <= len(hits)):
            selected_mods.append(hits[int(selected) - 1]["project_id"])
    return selected_mods


def output():
    if(ofilename == None):
        for l in operating_data:
            if(type(l) == list):
                print(f"{l[0]}::{l[1]}")
            else:
                print(l)
    else:
        try:
            f = open(ofilename, "w")
        except:
            print(f"Could not open file {ofilename}")
        for l in operating_data:
            if(type(l) == list):
                f.write(f"{l[0]}::{l[1]}\n")
            else:
                f.write(f"{l}\n")
        f.close()


if __name__ == "__main__":
    load_data()
    print(ofilename)
    if(search):
        do_search_action()
    output()    