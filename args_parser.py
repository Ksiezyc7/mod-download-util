import sys
argcn___ = 1
flags___ = []



def next_arg___():
    global argcn___
    if(argcn___ < len(sys.argv)):
        argcn___ += 1
        return sys.argv[argcn___ - 1]
    else:
        return None

def add_flag(name: str, aarg_c: int = 0):
    flags___.append((name, aarg_c))

def parse_args():
    arg = ""
    out = {"_" : []}
    while(arg != None):
        arg = next_arg___()
        if(arg == None):
            break
        flag = []
        for f in flags___:
            if(arg == f[0]):
                for c in range(f[1]):
                    flag.append(next_arg___())
                out[f[0]] = flag
                break
        else:
            out["_"].append(arg)
    return out
    