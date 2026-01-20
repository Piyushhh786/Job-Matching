# Website Analysis
1.) go to companies website
2.) open in inspect mode
3.) reload the page and find the api which got the data (search?*---); (This is the Gold)
e.g:https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com&query=&location=&start=0&


4.) inspect the request headers Look at:
Request URL
Request Method
Request Headers
Request Payload (if POST)

Example headers you NEED:
-User-Agent
-Referer
-Content-Type


# Getting URLs Structure

Google Custom Search
        ↓
Collect Workday URLs (job pages OR career pages)
        ↓
Normalize → Search-for-Jobs URL
        ↓
Store in DB
        ↓
Call /wday/cxs/ API
        ↓
Filter India + Intern
        ↓
Notify

### Note : have you done the llm part and then after resume maker???

# Database Design
sqlite> .tables
career_portals  job_matches     job_sentences   jobs

# Main.py :
##  a function which runs daily one time at morning or when we open(connected to internet) our laptop in a day  -> (searches for a job using job_api) if its

career_portals -> job_api -> send the post request with headers and get the intern job
once we got the intern and location should be not indiana or indianapolis
extract the job_description -> get_project_with_score if score > 51 then send the resume and job api to the main
