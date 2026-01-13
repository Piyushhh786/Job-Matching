# from serpapi import search
from serpapi import Client
import json

import os
path = "/storage/workdayjobs_urls.json"

client = Client(api_key="dcd40235d068e8a9a0e2cd385a32669449427186d1c8bf7e1458efacf78206c5")
# print(os.getenv("SERP_API_KEY"))

google_query= 'site:myworkdayjobs.com "india"'
print(os.path.exists(path))
if os.path.exists(path):
    with open(path,"r",encoding="utf-8")  as f:
        existing = json.load(f)
else: existing = {
    "direct_links": [],
    "undirect_links": []
}
print(existing)