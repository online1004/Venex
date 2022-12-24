from flask import Flask, render_template, request, session, redirect, abort, url_for
import sqlite3, json
import os
import uuid
import datetime
from datetime import timedelta
from util import funcs as fc, licensing
from discord_webhook import DiscordEmbed, DiscordWebhook

curdir = os.path.dirname(__file__) + "/"

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

def getip():
    return request.headers.get("CF-Connecting-IP", request.remote_addr)

@app.route("/discord")
def discord():
    return redirect("https://discord.gg/")

@app.route("/", methods=["GET"])
def index():
    if ("id" in session):
        return redirect(url_for("login"))
    else:
        return redirect(url_for("setting"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "GET"):
        if ("id" in session):
            return redirect(url_for("setting"))
        else:
            return render_template("login.html")
    else:
        if ("id" in request.form and "pw" in request.form):
            if (request.form["id"].isdigit() and os.path.isfile(curdir + "./db/" + request.form["id"] + ".db")):
                con = sqlite3.connect(curdir + "./db/" + request.form["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM info")
                serverinfo = cur.fetchone()
                if (request.form["pw"] == serverinfo[1]):
                    session.clear()
                    session["id"] = request.form["id"]
                    try:
                        cur.execute("SELECT * FROM webhook")
                        webhook = cur.fetchone()
                        webhook = DiscordWebhook(username='Venex System',
                                                 avatar_url='',
                                                 url=webhook[1])
                        eb = DiscordEmbed(title='웹패널 로그인 알림', description=f'[웹패널로 이동하기](http://127.0.0.1/)',
                                          color='#1454ff')
                        eb.add_embed_field(name='서버 아이디', value=session["id"], inline=False)
                        eb.add_embed_field(name='로그인 날짜', value=f"{licensing.nowstr()}", inline=False)
                        eb.add_embed_field(name='접속 IP', value=f"||{getip()}||", inline=False)
                        webhook.add_embed(eb)
                        webhook.execute()
                    except:
                        pass
                    return "Ok"
                else:
                    return "비밀번호가 틀렸습니다."
            else:
                return "아이디가 틀렸습니다."
        else:
            return "아이디가 틀렸습니다."

@app.route("/setting", methods=["GET", "POST"])
def setting():
    if (request.method == "GET"):
        if ("id" in session):
            con = sqlite3.connect("./db/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM info")
            serverinfo = cur.fetchone()
            cur.execute("SELECT * FROM webhook")
            webhook = cur.fetchone()
            con.close()
            return render_template("manage.html", info=serverinfo, webhook=webhook)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if (session["id"] != "495888018058510357"):
                if (request.form["buyusernamehide"] == "0" or request.form["buyusernamehide"] == "1"):
                        if (request.form["roleid"].isdigit()):
                                if request.form["webhookprofile"] != "":
                                        con = sqlite3.connect("./db/" + session["id"] + ".db")
                                        cur = con.cursor()
                                        cur.execute(
                                            "UPDATE info SET pw = ?, buyer = ?, toss = ?, hide = ?;",
                                            (request.form["webpanelpw"], request.form["roleid"],
                                                request.form['bankname'], request.form["buyusernamehide"],))
                                        con.commit()
                                        cur.execute(
                                            "UPDATE webhook SET buylog = ?, chargelog = ?, profile = ?;", (
                                                request.form["buylogwebhk"], request.form["buylogwebhk"], request.form["webhookprofile"]
                                            )
                                        )
                                        con.commit()
                                        con.close()
                                        return "ok"
                                else:
                                    return "웹훅 이름과 웹훅 프로필을 적어주세요."
                        else:
                            return "역할 아이디는 숫자로만 입력해주세요."
                else:
                    return "0 또는 1으로만 입력해주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/manage_user", methods=["GET"])
def manage_user():
    if ("id" in session):
        con = sqlite3.connect("./db/" + session["id"] + ".db")
        cur = con.cursor()
        cur.execute("SELECT * FROM user")
        users = cur.fetchall()
        con.close()
        return render_template("manage_user.html", users=users)
    else:
        return redirect(url_for("login"))

@app.route("/manage_user_detail", methods=["GET", "POST"])
def manageuser_detail():
    if (request.method == "GET"):
        if ("id" in session):
            user_id = request.args.get("id", "")
            if (user_id != ""):
                con = sqlite3.connect("./db/" + session["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM user WHERE id == ?;", (user_id,))
                user_info = cur.fetchone()
                con.close()
                if (user_info != None):
                    return render_template("manage_user_detail.html", info=user_info)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("money" in request.form and "id" in request.form):
                if (request.form["money"].isdigit()):
                        if (request.form["warnings"].isdigit()):
                                con = sqlite3.connect("./db/" + session["id"] + ".db")
                                cur = con.cursor()
                                cur.execute(
                                    "UPDATE user SET money = ?, warnings = ?, ban = ? WHERE id == ?;",
                                    (request.form["money"], request.form["warnings"], request.form["ban"], request.form["id"]))
                                con.commit()
                                con.close()
                                return "ok"
                        else:
                            return "문화상품권 충전 경고 수는 정수로만 적어주세요."
                else:
                    return "잔액은 정수로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/createprod", methods=["GET", "POST"])
def createprod():
    if (request.method == "GET"):
        if ("id" in session):
            return render_template("create_prod.html")
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("price" in request.form and "name" in request.form):
                if (request.form["price"].isdigit()):
                    con = sqlite3.connect("./db/" + session["id"] + ".db")
                    cur = con.cursor()
                    cur.execute("SELECT * FROM product WHERE name == ?;", (request.form["name"],))
                    prod = cur.fetchone()
                    if (prod == None):
                        con = sqlite3.connect("./db/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("INSERT INTO product VALUES(?, ?, ?);",
                                    (request.form["name"], request.form["price"], ""))
                        con.commit()
                        con.close()
                        return "ok"
                    else:
                        return "이미 존재하는 제품명입니다."
                else:
                    return "가격은 숫자로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/manage_product", methods=["GET"])
def manage_product():
    if ("id" in session):
        con = sqlite3.connect("./db/" + session["id"] + ".db")
        cur = con.cursor()
        cur.execute("SELECT * FROM product")
        products = cur.fetchall()
        con.close()
        return render_template("manage_prod.html", products=products)
    else:
        return redirect(url_for("login"))

@app.route("/delete_product", methods=["POST"])
def deleteprod():
    if ("id" in session):
        if ("name" in request.form):
            con = sqlite3.connect("./db/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("DELETE FROM product WHERE name == ?;", (request.form["name"],))
            con.commit()
            con.close()
            return "ok"
        else:
            return "fail"
    else:
        return "fail"

@app.route("/manage_product_detail", methods=["GET", "POST"])
def manage_product_detail():
    if (request.method == "GET"):
        if ("id" in session):
            product_name = request.args.get("id", "")
            if (product_name != ""):
                con = sqlite3.connect("./db/" + session["id"] + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM product WHERE name == ?;", (product_name,))
                prod_info = cur.fetchone()
                con.close()
                if (prod_info != None):
                    return render_template("manage_prod_detail.html", info=prod_info)
                else:
                    abort(404)
            else:
                abort(404)
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("price" in request.form and "stock" in request.form and "name" in request.form and "product_name" in request.form):
                if (request.form["price"].isdigit()):
                    con = sqlite3.connect("./db/" + session["id"] + ".db")
                    cur = con.cursor()
                    cur.execute(f"SELECT * FROM product WHERE name == '{request.form['product_name']}'")
                    result = cur.fetchone()
                    con.close()
                    if result == None:

                        con = sqlite3.connect("./db/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("UPDATE product SET name = ? WHERE name == ?;", (
                        request.form["product_name"], request.form["name"]))
                        con.commit()
                        con.close()

                        con = sqlite3.connect("./db/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute(f"SELECT * FROM product WHERE name == '{request.form['product_name']}';")
                        result = cur.fetchone()[2]
                        gop = str(result).split("\n")
                        con.close()

                        con = sqlite3.connect("./db/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("UPDATE product SET money = ?, stock = ? WHERE name == ?;", (
                        request.form["price"], request.form["stock"], request.form["name"]))
                        con.commit()
                        con.close()

                        finaa = str(request.form["stock"]).split("\n")
                        finnayl = int(len(finaa))-int(len(gop))

                    else:
                            con = sqlite3.connect("./db/" + session["id"] + ".db")
                            cur = con.cursor()
                            cur.execute(f"SELECT * FROM product WHERE name == '{request.form['product_name']}';")
                            result = cur.fetchone()[2]
                            gop = str(result).split("\n")
                            con.close()

                            con = sqlite3.connect("./db/" + session["id"] + ".db")
                            cur = con.cursor()
                            cur.execute("UPDATE product SET money = ?, stock = ? WHERE name == ?;", (
                            request.form["price"], request.form["stock"], request.form["name"]))
                            con.commit()
                            con.close()

                            return "ok"
                else:
                    return "가격은 숫자로만 적어주세요."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/license", methods=["GET", "POST"])
def managelicense():
    if (request.method == "GET"):
        if ("id" in session):
            con = sqlite3.connect("./db/" + session["id"] + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM info")
            serverinfo = cur.fetchone()
            con.close()
            if (licensing.is_expired(serverinfo[3])):
                return render_template("manage_license.html", expire="0일 0시간 (만료됨)")
            else:
                return render_template("manage_license.html", expire=licensing.get_remaining_string(serverinfo[3]))
        else:
            return redirect(url_for("login"))
    else:
        if ("id" in session):
            if ("code" in request.form):
                license_key = request.form["code"]
                con = sqlite3.connect("./db/" + "database.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                search_result = cur.fetchone()
                con.close()
                if (search_result != None):
                    if (search_result[2] == 0):
                        con = sqlite3.connect("./db/" + "database.db")
                        cur = con.cursor()
                        cur.execute("UPDATE license SET used = ? WHERE code == ?;", (1, license_key))
                        con.commit()
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                        key_info = cur.fetchone()
                        con.close()
                        con = sqlite3.connect("./db/" + session["id"] + ".db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM info;")
                        server_info = cur.fetchone()
                        if (licensing.is_expired(server_info[3])):
                            new_expiretime = licensing.make_new_expiringdate(key_info[1])
                        else:
                            new_expiretime = licensing.add_time(server_info[3], key_info[1])
                        cur.execute("UPDATE info SET expire = ?;", (new_expiretime,))
                        con.commit()
                        con.close()
                        return f"{key_info[1]}"
                    else:
                        return "이미 사용된 라이센스입니다."
                else:
                    return "존재하지 않는 라이센스입니다."
            else:
                return "잘못된 접근입니다."
        else:
            return "로그인이 해제되었습니다. 다시 로그인해주세요."

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html")

app.run(debug=False, host="0.0.0.0", port=80)