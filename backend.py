import requests

def query_mod():
    res = requests.request("GET", "http://localhost:8080/v2/search", params={"query" : "create", "limit" : 5, "facets" : "[[\"project_type=mod\"],[\"versions:1.21.11\"]]", })
    