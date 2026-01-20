from matcher.get_score import get_project_with_score # arguments job_description
from notifier.telegram import notify_telegram
import sqlite3
import requests as req
from datetime import datetime

db_path = r"E:\Desktop\webAutomation\job_agent.db"
conn  = sqlite3.connect(db_path)
cursor = conn.cursor()

header = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

def get_jd(url:str,p_id:int,title:str,threshold_days:int):
    res = req.get(url,headers=header)
    data = res.json()
    job = data.get('jobPostingInfo',[])
    job_description = ""
    job_description = job.get('jobDescription')
    location = ""
    location = (str)(job.get('location'))
    if "indianapolis" in location.lower() or "indiana" in location.lower(): return None,None
    date = ""
    date = job.get("startDate")
    if not date : 
        print("No startDate date Found!!")
        return None,None
    str_date = datetime.strptime(date,"%Y-%m-%d")
    curr_date = datetime.now()
    days_diff = (curr_date-str_date).days
    if days_diff > threshold_days : return None,None
    type = ""
    type = job.get('timeType')
    job_id = ""
    job_id = job.get('jobReqId')
    q = """select job_id,portal_id from jobs where job_id=? and portal_id=?"""
    if not job_id: 
        print("Job id not found!!")
        return None,None
    cursor.execute(q,(job_id,p_id))
    is_find = cursor.fetchone()
    print(f"is_find: {is_find}")
    if(is_find):
        print("This job is already done")
        return None,None
    q = """
            insert or ignore into jobs (employment_type,portal_id,title,job_id,apply_url,description,location,posted_date) 
            values (?,?,?,?,?,?,?,?) 
        """
    cursor.execute(q,(type,p_id,title,job_id,url,job_description,location,date))
    conn.commit()
    return job_description,days_diff


def get_jobs():
    threshold_days = 2
    q = """select job_api,portal_url,is_new,id from career_portals where job_api is not NULL"""
    cursor.execute(q)
    row = cursor.fetchall()

    for url,portal_url,is_new,p_id in row:
        print(f"[+] Fetching from: {portal_url}")
        i = 0
        total = 1

        if(is_new==1): 
            threshold_days = 5
            q = """update career_portals set is_new = ? where id = ?"""
            cursor.execute(q,(0,p_id))
            conn.commit()
        else: threshold_days = 2
    
        while((20*i)<min(total,150)):

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
                
                print(f"status: {res.status_code}, offset: {payload['offset']}")
                data = res.json()
                
                if(i==1): 
                    total = data['total']
                    print(f"Total Jobs in India Search: {total}")

                print(f"  -----------Success! Found {len(data.get('jobPostings', []))} jobs.")
                job_postings = data.get('jobPostings',[])
                # flag = False
                for job in job_postings:
                    ext_pth = job.get('externalPath')
                    if(not ext_pth) :
                        print(f"External Path is not in this {job.get('title')}")
                        continue
                    external_url = url[:-5]+ext_pth
                    apply_page = portal_url+ext_pth
                    title = job.get('title')
                    # if not 'intern' in title.lower() : continue # imp line for personal use

                    # --------- main code start from here -------------
                    jd,day_diff = get_jd(external_url,p_id,title,threshold_days)
                    if not jd : continue

                    resume_analyzer = get_project_with_score(jd) 
                    print(f"\nScore: {resume_analyzer['ats_score']}, url: {apply_page}\n")
                    if(resume_analyzer['ats_score']>50): notify_telegram(top_projects=resume_analyzer['top_projects'],job_url=apply_page,title=title)
                    else : continue


            except req.exceptions.RequestException as e:
                print(f"   [!] Error fetching {url} or inserting in jobs: {e}")
                break
get_jobs()
conn.close()


