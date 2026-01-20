import json
# from resume_generator.generator import generate_tex_file,compile_with_pdflatex
from resume_generator.generator import generate_resume
import requests as req
import os
from dotenv import load_dotenv,find_dotenv
env_file = find_dotenv()
load_dotenv(env_file)
TELE_TOKEN=os.getenv("TELE_TOKEN")
tele_token = "8425047043:AAH8L_UwdFDXLvUin4aipI_kHMr9x7cb41c"
http_req = f"https://api.telegram.org/bot{tele_token}/getUpdates"
chat_id = 1402439919
chat = {"id":1402439919,"first_name":"Prem","username":"Premm786","type":"private"}
resume_path = r"E:\Desktop\webAutomation\resume_generator\output\resume.pdf"

def notify_telegram(job_url,top_projects,title):
    generate_resume(top_projects=top_projects)
    try:
        text = (
            "🚀 *New Job Match Found!*\n\n"
            f"🔗 Apply URL:\n{job_url}\n\n"
            "📎 Resume attached below."
        )

        req.post(
            f"https://api.telegram.org/bot{tele_token}/sendMessage",
            json={
                "chat_id":chat_id,
                "text": text,
                "parse_mod":"Markdown"
            }
        )
        #   ------ send resume ------
        with open(resume_path,'rb') as f:
            
            req.post(
                f"https://api.telegram.org/bot{tele_token}/sendDocument",
                data = {"chat_id":chat_id},
                files= {"document":(f"{title}.pdf",f)}
            )
        #   ------ good formating ------
        line = "\n ------------------------------- ******** ------------------------------\n------------------------------- ******** ------------------------------"
        req.post(
            f"https://api.telegram.org/bot{tele_token}/sendMessage",
            json={
                "chat_id":chat_id,
                "text": line,
                "parse_mod":"Markdown"
            }
        )
        print("✅ Telegram notification sent")
    
    except Exception as e:
        print("❌ Telegram notification failed:",e)

