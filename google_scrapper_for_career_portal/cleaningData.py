import sqlite3
import re

db_path = r"E:\Desktop\webAutomation\job_agent.db"
conn  = sqlite3.Connection(db_path)

cursor = conn.cursor()


def cleaning() :
    cursor.execute("""
            select portal_url from career_portals
    """)
    row = cursor.fetchall()
    for (org_url,) in row:
        # org_url = "https://walmart.wd5.myworkdayjobs.com/WalmartExternal/details/SOFTWARE-ENGINEER-III_R-1773548?timeType=b181d8271e36017533d4ca68eee44f00&locationCountry=c4f78be1a8f14da0ab49ce1162348a5e"
        url = org_url
        url = re.sub(r"/[a-z]{2}-[A-Za-z]{2}","",url)
        parts = url.split("/")

    # join till WalmartExternal (index 3)
        new_url = "/".join(parts[:4])
        new_url = new_url.split("?")[0]
        print(new_url)
        print(org_url)
        # now delete that url and insert new url
        cursor.execute(""" delete from career_portals where portal_url = ? """,(org_url,))
        cursor.execute(""" insert or ignore into career_portals (portal_url) values (?) """,(new_url,))
    conn.commit()
    conn.close()

def remove_duplicates():
    cursor.execute("""
            select portal_url from career_portals
    """)
    row = cursor.fetchall()
    for (url,) in row:
        domain = url.split("/")[2]
        cursor.execute("""
                       delete from career_portals where portal_url != ? and portal_url like ?
        """,(url,f"%{domain}%"))
    conn.commit()

remove_duplicates()

