import requests as req
import sqlite3
import re
from datetime import datetime

db_path = r"E:\Desktop\webAutomation\job_agent.db"

conn = sqlite3.connect(db_path) 
cursor = conn.cursor()

header = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
threshold_days = 1

def insert_job_db(url,title,p_id) :
    try:
        res = req.get(url,headers=header)
        print(f"status: {res.raise_for_status()} for url: {url}")
        data = res.json()
        job = data.get('jobPostingInfo',[])
        job_description = ""
        job_description = job.get('jobDescription')
        location = ""
        location = (str)(job.get('location'))
        if "indianapolis" in location.lower() or "indiana" in location.lower(): return
        date = ""
        date = job.get("startDate")
        str_date = datetime.strptime(date,"%Y-%m-%d")
        curr_date = datetime.now()
        days_diff = (curr_date-str_date).days
        if days_diff > threshold_days : return 
        type = ""
        type = job.get('timeType')
        job_id = ""
        job_id = job.get('jobReqId')

        cursor.execute("""
            select * from jobs where job_id = ?
        """,(job_id,))
        isfind = cursor.fetchone() # if job already done then return no use of it

        if(isfind): return 

        cursor.execute("""
                insert or ignore into jobs (employment_type,portal_id,title,job_id,apply_url,description,location,posted_date) 
                    values (?,?,?,?,?,?,?,?) 
            """,(type,p_id,title,job_id,url,job_description,location,date))

        conn.commit()

    except req.exceptions.RequestException as e:
        print(f"    Getting error in fetching {url}: {e}")

cursor.execute("SELECT job_api,id,is_new FROM career_portals WHERE job_api IS NOT NULL")
db_data = cursor.fetchall()

for (url,p_id,is_new) in (db_data):
    print(f"[+] Fetching from: {url}")
    i = 0
    total = 1

    if(is_new==1): threshold_days = 5
    else: threshold_days = 1
    
    while((20*i)<total):

        payload = {
            "appliedFacets": {},
            "limit": 20,
            "offset": 20 * i, # Note i is page number
            "searchText": "india"
        }
        i+=1

        try:
            
            res = req.post(url, headers=header, json=payload, timeout=10)
            
            # This will jump to the 'except' block if the status is not 2xx
            res.raise_for_status() 
            
            print(f" status:  {res.raise_for_status()}, offset: {payload['offset']}")
            data = res.json()

            if(i==1): 
                total = data['total']
                print(f"Total Jobs in India Search: {total}")

            # here in future we uses ml model for which having attribute where we got all the jobs postings

            print(f"  -----------Success! Found {len(data.get('jobPostings', []))} jobs.")
            job_postings = data.get('jobPostings',[])
            flag = False
            for job in job_postings:
                ext_pth = job.get('externalPath')
                if(ext_pth): flag = True
                if(not ext_pth) : continue
                external_url = url[:-5]+ext_pth
                title = job.get('title')
                posted_on = job.get('postedOn')
                if(posted_on):
                    days = re.findall(r'\d+', job.get('postedOn'))
                    if(days and ((int)(days[0]) > threshold_days)) : continue
                insert_job_db(external_url,title,p_id)
            if flag == False : break

        except req.exceptions.RequestException as e:
            print(f"   [!] Error fetching {url} or inserting in jobs: {e}")
            break

conn.close()