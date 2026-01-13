
from serpapi import Client
import re
import sqlite3

# This file is used to updates the workday urls or add new workday url in the db
# in Future this will execute only once a month

client = Client(api_key="dcd40235d068e8a9a0e2cd385a32669449427186d1c8bf7e1458efacf78206c5")

google_query= 'site:myworkdayjobs.com "Pune" intitle:"Career"'
db_path = r"E:\Desktop\webAutomation\job_agent.db"

conn = sqlite3.Connection(db_path)
cursor = conn.cursor()


for i in range(0,300,10):

    s = client.search(q=google_query, location="India", hl='en', gl="in", start=i)
    if(s): print(f" Working iteration: {i}")

    for result in s.get("organic_results",[]):

        link = result.get('link')
        if not link: continue

        if "/job/" in link: link = link.split("/job/")[0]

        link = re.sub(r"/[a-z]{2}-[A-Za-z]{2}","",link) # remove #en-IN or any other format

        parts = link.split("/") # splitting based on /
        new_url = "/".join(parts[:4])

        link = new_url.split("?")[0] # removed external query

        # you have desired link now search on db is this present or not
        cursor.execute("""
            insert or ignore into career_portals (portal_url)
            values (?) 
        """,(link,))

    print(f"Done iteration: {i}")

conn.commit()
conn.close()