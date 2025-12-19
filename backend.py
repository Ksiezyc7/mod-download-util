import requests
import json

api_url = "https://api.modrinth.com/v2"
#api_url = "http://localhost:8000"
user_agent = "Ksiezyc7/mod-download-util"

def search_mod(query, limit, mc_ver):
    res = requests.request("GET", f"{api_url}/search", params={"query" : query, "limit" : limit, "facets" : f"[[\"project_type=mod\"],[\"versions:{mc_ver}\"]]", }, headers={"User-Agent" : user_agent})
    if(res.status_code != 200):
        return None
    json_data = res.json()
    if("hits" not in json_data or len(json_data["hits"]) <= 0):
        return None
    return json_data["hits"]
    