import sqlite3
from util import gen

amount = int(input('Amount : '))
date = int(input('date : '))

licenses = []

for _ in range(amount):
    code = "Venex-" + gen.gen(15)
    licenses.append(code)
    con = sqlite3.connect("./db/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO license Values(?, ?, ?);", (code, date, 0))
    con.commit()
    con.close()
    generated_key = "\n".join(licenses)

print("\n".join(licenses))