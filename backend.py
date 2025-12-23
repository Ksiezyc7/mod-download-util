import requests
import time

api_url = "https://api.modrinth.com/v2"
#api_url = "http://localhost:8000"
user_agent = "Ksiezyc7/mod-download-util"

_dependency_cache = {}
_download_cache = {}
_request_count = 0
_unit_prefixes = ["Ki", "Mi", "Gi", "Ti"]
def format_byte_count(c):
    p = 0
    cc = c
    for i in range(len(_unit_prefixes)):
        if(cc > 1024):
            cc = cc / 1024
            p += 1
        else:
            break
    if(p == 0):
        return f"{cc} B"
    else:
        return f"{"" if cc % 1 == 0 else "~"}{round(cc*10)/10} {_unit_prefixes[p-1]}B"

_org = 0
def start_timing():
    global _org
    _org = time.time_ns()

def record_timing():
    global _org
    r = time.time_ns() - _org
    _d_req_times.append(r/1000000)

_d_req_times = []
_d_req_data = []

_d_sent_reqs = 0
_d_cached_reqs = 0

def d_request_data():
    return _d_req_data

def d_request_time():
    return _d_req_times

def get_req_count():
    return _request_count

def search_mod(query, limit, mc_ver, loader):
    global _request_count
    global _d_cached_reqs
    global _d_sent_reqs
    if(mc_ver != "*"):
        start_timing()
        res = requests.request("GET", f"{api_url}/search", params={"query" : query, "limit" : limit, "facets" : f"[[\"project_type=mod\"],[\"versions:{mc_ver}\"],[\"categories:{loader}\"]]", }, headers={"User-Agent" : user_agent})
        _request_count += 1
        _d_sent_reqs += 1
        _d_req_data.append(len(res.content))
        record_timing()
    else:
        start_timing
        res = requests.request("GET", f"{api_url}/search", params={"query" : query, "limit" : limit, "facets" : f"[[\"project_type=mod\"],[\"categories:{loader}\"]]", }, headers={"User-Agent" : user_agent})
        _request_count += 1
        _d_sent_reqs += 1
        _d_req_data.append(len(res.content))
        record_timing()
    
    
    if(res.status_code != 200):
        return None
    json_data = res.json()
    if("hits" not in json_data or len(json_data["hits"]) <= 0):
        return None
    return json_data["hits"]
def get_newest_version_that_supports_minecraft_v(project_id: str, mcv: str, loader: str):
    global _request_count
    global _d_cached_reqs
    global _d_sent_reqs

    start_timing()
    res = requests.request("GET", f"{api_url}/project/{project_id}/version", params={"loaders" : f"[\"{loader}\"]", "game_versions" : f"[\"{mcv}\"]"}, headers={"User-Agent" : user_agent})
    _request_count += 1
    _d_sent_reqs += 1
    _d_req_data.append(len(res.content))
    record_timing()


    if(res.status_code != 200):
        return None
    json_data = res.json()



    if(len(json_data) > 0):
        ver = json_data[0]["id"]
        if(ver not in _dependency_cache.keys()):
            _dependency_cache[ver] = json_data[0]["dependencies"]
        if(ver not in _download_cache.keys()):
            _download_cache[ver] = {"url" : json_data[0]["files"][0]["url"], "filename" : json_data[0]["files"][0]["filename"]}

        return [json_data[0]["project_id"], json_data[0]["id"]]
    return None
    pass

def get_dependencies(version_id):
    if(version_id == None):
        return None
    global _request_count
    global _d_cached_reqs
    global _d_sent_reqs

    
    if(version_id in _dependency_cache):
        a = []
        for d in _dependency_cache[version_id]:
            a.append([d["project_id"], d["version_id"]])
        _d_cached_reqs += 1
        return a

    start_timing()
    res = requests.request("GET", f"{api_url}/version/{version_id}", headers={"User-Agent" : user_agent})
    _request_count += 1
    _d_sent_reqs += 1
    _d_req_data.append(len(res.content))
    record_timing()

    if(res.status_code != 200):
        return None
    json_data = res.json()

    if("dependencies" in json_data):
        if(version_id not in _dependency_cache.keys()):
            _dependency_cache[version_id] = json_data["dependencies"]
        a = []
        for d in json_data["dependencies"]:
            a.append([d["project_id"], d["version_id"]])
        return a
    return None
def get_download_data(ver_id):
    global _d_cached_reqs
    global _d_sent_reqs
    
    if(ver_id in _download_cache):
        _d_cached_reqs += 1
        return _download_cache[ver_id]
    else:
        return None
    
def download_file(url, filename):
    global _request_count
    global _d_cached_reqs
    global _d_sent_reqs

    res = requests.request("GET", url, headers={"User-Agent" : user_agent})
    _request_count += 1
    _d_sent_reqs += 1
    _d_req_data.append(len(res.content))
    if(res.status_code != 200):
        return


    with open(filename, "wb") as file:
        file.write(res.content)



def d_total_data():
    a = 0
    for i in _d_req_data:
        a += i
    return a

def d_avg_req_time_ms():
    a = 0
    c = 0
    for i in _d_req_times:
        a += i
        c += 1
    return a / c

def d_total_req_time_ms():
    a = 0
    for i in _d_req_times:
        a += i
    return a

def d_cached_reqs():
    return _d_cached_reqs

def d_sent_reqs():
    return _d_sent_reqs