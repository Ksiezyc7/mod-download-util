import requests
import defs
from backend import *
from args_parser import *
import re
import time

_mod_count = 0

add_flag("-s") # Search
add_flag("-g") # Get version id
add_flag("-f") # Find dependencies
add_flag("-d") # Download
add_flag("-o", 1) # output file, defaults to "mods.txt"
add_flag("-c", 1) # amount of search hits to show
add_flag("-v", 1) # minecraft version
add_flag("-l", 1) # minecraft loader
add_flag("-u") # output URLs
add_flag("~~") # Do diagnostics

add_flag("-r", 1) # dependency recursion depth

add_flag("-h") # Help

ofilename = "mods.txt"

output_urls = False

ifilename = ""
top_c = 5 # amount of hits to show, defaults to 5
mc_loader = None
m_version = "1.21.11" # minecraft version to search for, defaults to newest, as of 17.12.2025 it's 1.21.11
dependecy_search_recursion_depth = 2


def display_help_text():
    time.sleep(0.01)
    print("Usage:")
    time.sleep(0.01)
    print("$ py modutil.py <modlistfile> [flags]")
    time.sleep(0.01)
    print("")
    time.sleep(0.01)
    print("Actions:\n")
    time.sleep(0.01)
    print("There are 4 actions: search, get_version, find_dependencies and download\nThey can be run separately or one after the other\nin that case the next action fill use the result of the previous one\nactions must be run in order search, get_version, (find_dependencies), download\nfind_dependencies is optional but recomended\n")
    time.sleep(0.01)
    print("Flags:\n")
    time.sleep(0.01)
    print("-s - Search\npreforms the search action\n")
    time.sleep(0.01)
    print("-g - Get version\npreforms the get_version action\n")
    time.sleep(0.01)
    print("-f - Find dependencies\npreforms the find_dependencies action\n")
    time.sleep(0.01)
    print("-d - Download\npreforms the download action\n")
    time.sleep(0.01)
    print("-o <out_file> - Output\nsets output file name, pass . as argument to print to console\n")
    time.sleep(0.01)
    print("-c <max_count> - max hit Count\namount of hits to show when searching (capped at 20), pass 1 to automatically choose first hit\n")
    time.sleep(0.01)
    print("-v <version> - Version\nchooses which Minecraft version to use when searching or getting version (defaults to newest mc version), pass * to search for any version\n")
    time.sleep(0.01)
    print("-l <loader> - Loader\nsets which mod loader to search mods for\n")
    time.sleep(0.01)
    print("-u - output URLs\noutputs URLs rather than ids\n")
    time.sleep(0.01)
    print("-r - Recursion depth\nrecursion depth for dependency searching\n")
    time.sleep(0.01)
    print("-h - Help\ndisplays this text\n")
    time.sleep(0.01)
    print("Add ~~ as one of the arguments to get extra diagnostics info")







args = parse_args()
if("-h" in args):
    display_help_text()
    exit()


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

if("-r" in args):
    if(args["-r"][0] == None):
        dependecy_search_recursion_depth = 2
    else:
        dependecy_search_recursion_depth = int(args["-r"][0]) if args["-r"][0].isnumeric() else 2


# What actions to do

search = "-s" in args.keys()
get_version = "-g" in args.keys()
find_dependecies = "-f" in args.keys()
download = "-d" in args.keys()

output_urls = "-u" in args.keys()

do_diagnostics = "~~" in args.keys()

if(search and download and not get_version):
    get_version = True
    print("Actions do not follow order")
    print("search\nget_version # MISSING\ndownload\n")
    print("get_version will be executed implicitly")

if(not (search or find_dependecies or download)):
    print("No action specified!")
    print("use -h to see actions\n")
    exit()

# Validate some provided data

top_c = max(1, min(top_c, 20)) # Clamp the max hit count between 1 and 20
dependecy_search_recursion_depth = max(1, min(dependecy_search_recursion_depth, 7))

# M
known_loaders = ["forge", "fabric", "neoforge", "quilt"]

# Download action uses already known mod ids and version ids so if the user is only downloading there is no need to verify these variables

print("")

if(search or get_version or find_dependecies):
    if(mc_loader == None):
        print("Mod loader not specified!\n")
        print("Specify a loader with the -l flag\n")
        print("Most common loaders:")
        print("forge, fabric, neoforge, quilt")
        exit(2)
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
    global _mod_count
    try:
        f = open(ifilename, "r")
    except FileNotFoundError:
        print(f"Could not open file {ifilename}")
        exit(1)
    for line in f.readlines():
        if("::" in line):
            a = line.strip("\n\r").split("::", 1)
            if(a[1] == "__null__"):
                a[1] = None
            operating_data.append(a)
        else:
            operating_data.append(line.strip("\n\r"))
    _mod_count = len(operating_data)

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
    operating_data = search_multiple(operating_data)

def do_get_version_action():
    global operating_data
    m = []
    for i in operating_data:
        print(f"Finding version for {i}...")
        a = get_newest_version_that_supports_minecraft_v(i, m_version, mc_loader)
        if(a == None):
            print(f"Could not find matching version for mod id {i}")
            continue
        m.append(a)
    operating_data = m
    pass
def remove_duplicates(l):
    a = []
    k = []
    for i in l:
        if(i[0] not in k):
            a.append(i)
            k.append(i[0])
    return a

def do_find_dependencies_action():
    global operating_data
    a = []
    print("Searching dependencies...")
    for _ in range(dependecy_search_recursion_depth):
        print(f"Iteration ({_+1}/{dependecy_search_recursion_depth})")
        for m in operating_data:
            v = get_dependencies(m[1])
            a = a + v if v != None else []
        operating_data = operating_data + a
    operating_data = remove_duplicates(operating_data)

def denullify_version():
    for i in range(len(operating_data)):
        if(operating_data[i][1] == None):
            operating_data[i][1] = get_newest_version_that_supports_minecraft_v(operating_data[i][0], m_version, mc_loader)[1]



def do_download_action():
    global operating_data
    m = []
    denullify_version()
    for i in operating_data:
        m.append(get_download_data(i[1]))
    operating_data = m
    
    if(output_urls):
        mm = []
        for i in operating_data:
            mm.append(i["url"])
        operating_data = mm
        return    
    print(f"Are you sure you want do download {len(operating_data)} file{"s" if len(operating_data) > 1 else ""} Y/n")
    choice = input("> ")
    if(len(choice) > 0 and choice[0].lower() == "n"):
        pass
    else:
        for f in operating_data:
            print(f"Downloading {f["filename"]}")
            download_file(f["url"], f["filename"])
        operating_data = []



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
            if(output_urls):
                if(l[1] == None):
                    out_text(f"https://modrinth.com/mod/{l[0]}\n")
                else:
                    out_text(f"https://modrinth.com/mod/{l[0]}/version/{l[1]}\n")
            else:
                out_text(f"{l[0]}::{l[1] if l[1]!=None else "__null__"}\n")
        else:
            if(output_urls):
                out_text(f"https://modrinth.com/mod/{l}\n")
            else:
                out_text(f"{l}\n")




if __name__ == "__main__":
    global _request_count

    load_data()
    if(search):
        do_search_action()
        print("")
    if(get_version):
        do_get_version_action()
        print("")
    if(find_dependecies):
        do_find_dependencies_action()
        print("")
    if(download):
        do_download_action()
    output()  
    print(f"\nFinished succesfully with {get_req_count()} request{"s" if get_req_count() > 1 else ""} made, ~{round((get_req_count()/_mod_count)*10)/10} per mod")
    if(do_diagnostics):
        print("\n\n[ Extra diagnostics information ]\n")
        print(f"Total data recived: {format_byte_count(d_total_data())} ({d_total_data()} B)")
        print(f"Average request time: ~{round(d_avg_req_time_ms())} ms")
        print(f"Average transfer rate: {format_byte_count(d_total_data() / (d_total_req_time_ms()/1000))}/s")
        print("")
        print(f"Of {d_sent_reqs()+d_cached_reqs()} requests:")
        if(d_sent_reqs() > d_cached_reqs()):
            print(f"    {d_sent_reqs()} ({round(d_sent_reqs() / (d_sent_reqs()+d_cached_reqs()) * 100)}%) sent to server")
            print(f"    {d_cached_reqs()} ({round(d_cached_reqs() / (d_sent_reqs()+d_cached_reqs()) * 100)}%) answered from cache")
        else:
            print(f"    {d_cached_reqs()} ({round(d_cached_reqs() / (d_sent_reqs()+d_cached_reqs()) * 100)}%) answered from cache")
            print(f"    {d_sent_reqs()} ({round(d_sent_reqs() / (d_sent_reqs()+d_cached_reqs()) * 100)}%) sent to server")