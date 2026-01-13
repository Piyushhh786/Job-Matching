import os
import json
from urllib.parse import urlparse
import sqlite3
db_path = "E:\Desktop\webAutomation\job_agent.db"
path = "E:\Desktop\webAutomation\storage\myworkdayjobs_urls.json"

with open(path,'r',encoding='utf-8') as f:
    sources = json.load(f)
urls = list(sources.get('URLs',[]))


conn = sqlite3.connect(db_path)
cursor = conn.cursor()

c = 0

for link in urls:
    try:
        # company,domain = makeCompaniesTable(link)

        # cursor.execute("""
        #         insert or ignore into companies (name,domain,category)
        #         values (?,?,?)
        # """,(company,domain,'workday'))

        # cursor.execute("""
        #         select id from companies where name = ?
        # """,(company,))
        # company_id = cursor.fetchone()[0]

        cursor.execute("""
            insert or ignore into career_portals (portal_url)
            values (?) 
        """,(link,))

    except Exception as e:
        print(f"failed for url: {link}: {e}")
        c=c+1
print(c)
conn.commit()
conn.close()
print(f"Inserted {len(urls)} portals into database")

    

