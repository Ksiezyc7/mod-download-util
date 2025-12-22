import requests
import json

api_url = "https://api.modrinth.com/v2"
#api_url = "http://localhost:8000"
user_agent = "Ksiezyc7/mod-download-util"

_dependency_cache = {}
_download_cache = {}
_request_count = 0
def get_req_count():
    return _request_count

def search_mod(query, limit, mc_ver, loader):
    global _request_count
    if(mc_ver != "*"):
        res = requests.request("GET", f"{api_url}/search", params={"query" : query, "limit" : limit, "facets" : f"[[\"project_type=mod\"],[\"versions:{mc_ver}\"],[\"categories:{loader}\"]]", }, headers={"User-Agent" : user_agent})
        _request_count += 1
    else:
        res = requests.request("GET", f"{api_url}/search", params={"query" : query, "limit" : limit, "facets" : f"[[\"project_type=mod\"],[\"categories:{loader}\"]]", }, headers={"User-Agent" : user_agent})
        _request_count += 1
    
    
    if(res.status_code != 200):
        return None
    json_data = res.json()
    if("hits" not in json_data or len(json_data["hits"]) <= 0):
        return None
    return json_data["hits"]
def get_newest_version_that_supports_minecraft_v(project_id: str, mcv: str, loader: str):
    global _request_count
    res = requests.request("GET", f"{api_url}/project/{project_id}/version", params={"loaders" : [loader], "game_versions" : [mcv]}, headers={"User-Agent" : user_agent})
    _request_count += 1
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
    global _request_count
    if(version_id in _dependency_cache):
        a = []
        for d in _dependency_cache[version_id]:
            a.append([d["project_id"], d["version_id"]])
        return a

    res = requests.request("GET", f"{api_url}/version/{version_id}", headers={"User-Agent" : user_agent})
    _request_count += 1
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