import sqlite3
import datetime
from datetime import timedelta
from util import gen

def make_new_expiringdate(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def create(license, guild_id):
    pw = gen.gen(10)
    exdate = sqlite3.connect("./db/database.db").cursor().execute("SELECT * FROM license WHERE code == ?;", (license,)).fetchone()[1]
    expire = make_new_expiringdate(int(exdate))
    con = sqlite3.connect(f"./db/{guild_id}.db")
    cur = con.cursor()
    cur.execute("""
                CREATE TABLE info (
                    id INTEGER, 
                    pw TEXT,
                    buyer INTEGER,
                    expire TEXT, 
                    cultureid TEXT, 
                    culturepw TEXT, 
                    fee INTEGER, 
                    toss TEXT,
                    hide INTEGER);
                """)
    cur.executemany("INSERT INTO info VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", [(guild_id, pw, 0, expire, "", 0, "", "", 0)])
    con.commit()
    cur.execute("CREATE TABLE product (name TEXT, money INTEGER, stock TEXT);")
    con.commit()
    cur.execute("CREATE TABLE user (id INTEGER, money INTEGER, warnings INTEGER, ban INTEGER);")
    con.commit()
    cur.execute("CREATE TABLE webhook (buylog TEXT, chargelog TEXT, profile TEXT);")
    con.commit()
    cur.execute("INSERT INTO webhook VALUES(?, ?, ?)", ("", "", "") )
    con.commit()
    con.close()

    con = sqlite3.connect("./db/database.db")
    cur = con.cursor()
    cur.execute("UPDATE license SET used = ? WHERE code == ?;", (1, license))
    con.commit()
    con.close()
    return pw, expire, exdate

def user_data(guild_id, user_id):
    con = sqlite3.connect(f'./db/{guild_id}.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM user WHERE id == ?;", (user_id,))
    result = cur.fetchone()
    return result

def toss(guild_id):
    con = sqlite3.connect(f'./db/{guild_id}.db')
    cur = con.cursor()
    cur.execute(f"SELECT * FROM info WHERE id = '{guild_id}'")
    result = cur.fetchone()
    return result[6]

def add_money(guild_id, user_id, money):
    con = sqlite3.connect(f'./db/{guild_id}.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE id = {user_id}')
    result = cur.fetchone()
    last_m = result[1]
    new_m = int(last_m) + int(money)
    cur.execute("UPDATE user SET money = ? WHERE id == ?;", (new_m, user_id))
    con.commit()
    cur.execute(f'SELECT * FROM user WHERE id = {user_id}')
    result = cur.fetchone()
    con.close()
    return result[1] # 최종적으로 추가된 금액을 리턴함