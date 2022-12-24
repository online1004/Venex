import sqlite3
import os
from util import licensing
import discord


def embed(embedtype, embedtitle, description):
    if (embedtype == "error"):
        return discord.Embed(color=0xff0000, title=embedtitle, description=description)
    if (embedtype == "success"):
        return discord.Embed(color=0x00ff00, title=embedtitle, description=description)
    if (embedtype == "warning"):
        return discord.Embed(color=0xffff00, title=embedtitle, description=description)


def start_db(id=0):
    if id == 0:
        con = sqlite3.connect("license.db")
        cur = con.cursor()
    else:
        con = sqlite3.connect(f"DB/{str(id)}.db")
        cur = con.cursor()

    return con, cur


def is_guild_valid(id):
    if os.path.isfile(f"DB/{str(id)}.db"):
        con, cur = start_db(id)
        cur.execute("SELECT * FROM configs;")
        configs = cur.fetchone()
        con.close()
        if licensing.is_expired(configs[0]):
            return (True, False)
        else:
            return (True, True)
    else:
        return (False, False)


def guild_info(id):
    if not is_guild_valid(id)[0]:
        return None
    con, cur = start_db(id)
    cur.execute("SELECT * FROM configs;")
    configs = cur.fetchone()
    con.close()
    return configs


def guild_users(id):
    if not is_guild_valid(id)[0]:
        return None
    con, cur = start_db(id)
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    con.close()
    return users


def guild_user(guild_id, user_id):
    if not is_guild_valid(guild_id)[0]:
        return None
    con, cur = start_db(guild_id)
    cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
    user = cur.fetchone()
    con.close()
    return user


def guild_products(id):
    if not is_guild_valid(id)[0]:
        return None
    con, cur = start_db(id)
    cur.execute("SELECT * FROM products;")
    products = cur.fetchall()
    con.close()
    return products


def guild_product(guild_id, product_id):
    if not is_guild_valid(guild_id)[0]:
        return None
    con, cur = start_db(guild_id)
    cur.execute("SELECT * FROM products WHERE id == ?;", (product_id,))
    product = cur.fetchone()
    con.close()
    return product