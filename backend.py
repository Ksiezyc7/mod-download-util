import requests
import json

api_url = "https://api.modrinth.com/v2"
#api_url = "http://localhost:8000"
user_agent = "Ksiezyc7/mod-download-util"

def search_mod(query, limit, mc_ver, loader):
    if(mc_ver != "*"):
        res = requests.request("GET", f"{api_url}/search", params={"query" : query, "limit" : limit, "facets" : f"[[\"project_type=mod\"],[\"versions:{mc_ver}\"],[\"categories:{loader}\"]]", }, headers={"User-Agent" : user_agent})
    else:
        res = requests.request("GET", f"{api_url}/search", params={"query" : query, "limit" : limit, "facets" : f"[[\"project_type=mod\"],[\"categories:{loader}\"]]", }, headers={"User-Agent" : user_agent})

    
    
    if(res.status_code != 200):
        return None
    json_data = res.json()
    if("hits" not in json_data or len(json_data["hits"]) <= 0):
        return None
    return json_data["hits"]
def get_newest_version_that_supports_minecraft_v(project_id: str, mcv: str, loader: str):
    res = requests.request("GET", f"{api_url}/project/{project_id}/version", params={"loaders" : [loader], "game_versions" : [mcv]}, headers={"User-Agent" : user_agent})
    if(res.status_code != 200):
        return None
    json_data = res.json()
    pass

def get_dependencies(project_id):
    res = requests.request("GET", f"{api_url}/project/{project_id}/dependencies", headers={"User-Agent" : user_agent})

    return json.dumps(res.json(), indent=4)