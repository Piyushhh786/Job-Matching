# This file is for getting the job_api for career_portals (workday url)
## every career_portals having single job_api

# run after getting new career_portals (: after running google_scrapper_for_carrer_portal)
from seleniumwire import webdriver
import sqlite3

driver = webdriver.Chrome()

db_path = r"E:\Desktop\webAutomation\job_agent.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT portal_url FROM career_portals where job_api is null
""")

rows = cursor.fetchall()
for (portal_url,) in rows:
    print(f"[+] Visiting {portal_url}")
    
    # 1. Clear existing requests completely (imp)
    del driver.requests 
    
    driver.get(portal_url)
    
    try:
        # This waits up to 20 seconds for a URL containing 'jobs' to appear
        request = driver.wait_for_request('/jobs', timeout=20)
        print(f"Request: {request}")

        if request.method == 'POST':
            job_api = request.url
            print("    Found API:", job_api)
            
            # UPDATE DATABASE
            cursor.execute("""
                UPDATE career_portals
                SET job_api = ?
                WHERE portal_url = ?
            """, (job_api, portal_url))

            conn.commit()
        else:
            print("    Found 'jobs' but it wasn't a POST request.")
            
    except Exception as e:
        print(f"    ------ No API found for {portal_url} ------")

driver.quit()
conn.close()
