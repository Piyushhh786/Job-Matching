
import sqlite3
from normalizer.preprocess_data import extract_sentences_from_html,is_imp
from joblib import Parallel, delayed

# In this file we are making label data for our classification model
## Storing that data in job_agent.db inside a job_sentences
### html description (job table) -> extract sentences -> important or not (hueristic approach)
### sentence -> job_sentences table with label 0/1

db_path = r"E:\Desktop\webAutomation\job_agent.db"

conn = sqlite3.connect(db_path)

cursor = conn.cursor()
cursor.execute("""
    select description, job_id,portal_id from jobs
""")

rows = cursor.fetchall()

imp_sent = set()
not_imp_sent = set()

def extract_sentences(row):
    des,j_id,p_id = row
    
    sentences = extract_sentences_from_html(des)

    for s in sentences:
        if(is_imp(s)): imp_sent.add((s,j_id,p_id))
        else : not_imp_sent.add((s,j_id,p_id))

Parallel(n_jobs=-1,backend="threading")(
    delayed(extract_sentences)(rows[i]) for i in range(0,len(rows))
)
try:

    for (s,j_id,p_id) in imp_sent:

        cursor.execute("""
                insert or ignore into job_sentences (job_id,sentence,portal_id,importance_label) values(?,?,?,?)
        """,(j_id,s,p_id,1))

        print(f"Successfully added imp_sent: {j_id}, {p_id}")

    for (s,j_id,p_id) in not_imp_sent:

        cursor.execute("""
                insert or ignore into job_sentences (job_id,sentence,portal_id,importance_label) values(?,?,?,?)
        """,(j_id,s,p_id,0))

        print(f"Successfully added not_imp_sent: {j_id}, {p_id}")

except sqlite3.IntegrityError as e:
    print("Integrity error (likely duplicate sentence):", e)

except sqlite3.OperationalError as e:
    print("SQL error (schema / column / syntax issue):", e)

except Exception as e:
    print("Unexpected error:", e)

print(len(imp_sent),len(not_imp_sent))

conn.commit()
conn.close()
