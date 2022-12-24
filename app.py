# coding=utf-8

import nextcord, sqlite3, os
import datetime
from datetime import timedelta
from nextcord.ext import commands, menus
from nextcord.ui import View
from config import token, GUILD_ID
from util import database, toss

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

buying = []

@bot.event
async def on_ready():
    print('Venex - 성공적으로 시스템이 시작됨')

@bot.event
async def on_message(message):
    if message.content.startswith('.등록 '):
        if isinstance(message.channel, nextcord.channel.DMChannel):
            return await message.channel.send('해당 채널에선 명령어를 사용하실 수 없습니다.')
        if not message.author.guild_permissions.administrator:
            return await message.channel.send('당신은 해당 명령어를 사용할 권한이 없습니다.')
        license = str(message.content.split(" ")[1])
        con = sqlite3.connect(f'./db/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM license WHERE code == ?;", (license,))    
        result = cur.fetchone()
        con.close()
        if result == None: 
            return await message.channel.send(embed = nextcord.Embed(
                title="서버 등록 실패",
                description=f"**```css\n[ ⛔ ] 존재하지 않는 라이센스입니다.```**"
            ))
        if result[2] == 1:
            return await message.channel.send(embed = nextcord.Embed(
                title="서버 등록 실패",
                description=f"**```css\n[ ⛔ ] 이미 사용된 라이센스입니다.```**"
            ))
        if result[2] == 0:
            if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                return await message.channel.send(embed = nextcord.Embed(
                title="서버 등록 실패",
                description=f"**```css\n[ ⛔ ] 이미 등록된 서버입니다.```**"
            ))
            data = database.create(license, message.guild.id)
            embed = nextcord.Embed(
                title="서버 등록 성공",
                description=f"**```css\n[ ✅ ] 서버 등록을 성공하였습니다.\n등록기간 : {data[2]} 일\n만료일 : {data[1]}\n비밀번호 : {data[0]}```**"
            )
            await message.author.send(embed=embed)
            embed = nextcord.Embed(
                title='서버 등록 성공',
                description=f"**```css\n[ ✅ ] 디엠을 확인해주세요 !```**"
            )
            await message.channel.send(embed=embed)

    if message.content == '.백업':
        if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
            if message.author.guild_permissions.administrator:
                try:
                    await message.channel.send(file=nextcord.File(f"./db/{message.guild.id}.db"))
                except:
                    await message.channel.send(embed = nextcord.Embed(
                        title="데이터베이스 백업 실패",
                        description="**```css\n[ ⛔ ] 용량이 너무 크거나 오류가 발생하였습니다.```**"
                    ))

@bot.slash_command(description=f"자판기 가입하기", guild_ids=[GUILD_ID])
async def 가입(interaction: nextcord.Interaction):
    await interaction.send(embed= nextcord.Embed (
        title='가입 시도 중 ...',
        description='**```css\n[ 🔎 ] 가입을 시도하고 있습니다...```**'
    ), ephemeral=True)
    if not (os.path.isfile("./db/" + str(interaction.guild_id) + ".db")):
        return await interaction.edit_original_message(embed= nextcord.Embed(
            title='가입 실패',
            description='**```css\n[ ⛔ ] 등록되지 않은 서버입니다.```**'
        ))
    result = database.user_data(interaction.guild_id, interaction.user.id)
    if not result == None: 
        return await interaction.edit_original_message(embed= nextcord.Embed (
            title='가입 실패',
            description='**```css\n[ ⛔ ] 이미 가입된 유저입니다.```**'
        ))
    con = sqlite3.connect(f'./db/{interaction.guild_id}.db')
    cur = con.cursor()
    cur.execute("INSERT INTO user VALUES(?, ?, ?, ?)", (interaction.user.id, "0", "0", "0"))
    con.commit()
    con.close()
    embed = nextcord.Embed(
        title = '가입 성공 알림',
        description= '**```css\n[ ✅ ] 가입이 성공적으로 완료되었습니다!```**'
    )
    await interaction.edit_original_message(embed=embed)

@bot.slash_command(description=f"내정보 확인하기", guild_ids=[GUILD_ID])
async def 내정보(interaction: nextcord.Interaction):
    await interaction.send(embed= nextcord.Embed (
        title='정보 확인 시도 중 ...',
        description='**```css\n[ 🔎 ] 정보 확인을 시도하고 있습니다...```**'
    ), ephemeral=True)
    if not (os.path.isfile("./db/" + str(interaction.guild_id) + ".db")):
        return await interaction.edit_original_message(embed= nextcord.Embed(
            title='가입 실패',
            description='**```css\n[ ⛔ ] 등록되지 않은 서버입니다.```**'
        ))
    result = database.user_data(interaction.guild_id, interaction.user.id)
    if result == None: 
        return await interaction.edit_original_message(embed= nextcord.Embed (
            title='정보 확인 실패',
            description='**```css\n[ ⛔ ] 가입되지 않은 유저입니다.```**'
        ))  
    embed = nextcord.Embed(
        title = '정보 확인 성공 알림',
        description= f'**```css\n[ ✅ ] 정보 확인이 성공적으로 완료되었습니다!\n\n[ 닉네임 ] {bot.get_user(result[0])} 님 \n[ 잔액 ] {result[1]} 원\n[ 경고수 ] {result[2]} 회\n[ 차단여부 ] {result[3]} 회```**'
    )
    await interaction.edit_original_message(embed=embed)

@bot.slash_command(description=f"계좌이체 자동충전", guild_ids=[GUILD_ID])
async def 계좌이체(interaction: nextcord.Interaction, 충전금액:int):
    await interaction.send(embed = nextcord.Embed(
        title='계좌이체 자동충전 알림',
        description='**```css\n[ 🔎 ] 계좌이체 자동충전을 시도하고 있습니다...```**'
    ), ephemeral=True)
    if not (os.path.isfile("./db/" + str(interaction.guild_id) + ".db")):
        return await interaction.edit_original_message(embed= nextcord.Embed(
            title='충전 실패',
            description='**```css\n[ ⛔ ] 등록되지 않은 서버입니다.```**'
        ))
    result = database.user_data(interaction.guild_id, interaction.user.id)
    if result == None: 
        return await interaction.edit_original_message(embed= nextcord.Embed (
            title='정보 확인 실패',
            description='**```css\n[ ⛔ ] 가입되지 않은 유저입니다.```**'
        ))  
    result = toss.request(database.toss(interaction.guild_id), 충전금액)
    if result == 'FAIL':
        return await interaction.edit_original_message(embed= nextcord.Embed(
            title='계좌이체 실패 알림',
            description='**```css\n[ ⛔ ] 문제가 발생하였습니다. 관리자에게 문의해주세요.```**'
        ))
    class confirm(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.value = None
        @nextcord.ui.button(label = '이체확인', style=nextcord.ButtonStyle.green, custom_id=result[0])
        async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
            self.value = True
            self.stop()
    view = confirm()
    await interaction.edit_original_message(embed= nextcord.Embed(
        title='계좌 충전 요청',
        description=f'**사용법**\n```1. 입금자명을 {result[0]} 으로 변경해주세요.\nㄴ 올바르게 변경하지 않은 경우 충전이 실패됩니다.\n1. {result[1]} 로 {충전금액} 원을 입금해주세요.\n3. 이체를 완료하신 뒤 아래 버튼을 눌러주세요.\n4. 요청은 5분 후 만료되니 주의해주세요 !```'
    ), view=view)
    await view.wait()
    if view.value:
        con_res = toss.confirm(result[0])
        if con_res[0] == 'FAIL':
            return await interaction.edit_original_message(embed= nextcord.Embed(
                title='계좌이체 실패 안내',
                description=f'**```css\n[ ⛔ ] {con_res[1]}```**'
            ), view=None)
        database.add_money(interaction.guild_id, interaction.user.id, con_res[1])
        await interaction.edit_original_message(embed= nextcord.Embed(
                title='계좌이체 성공 안내',
                description=f'**```css\n[ ✅ ] {con_res[1]} 원이 성공적으로 충전되었습니다.\n\n/내정보 를 입력하여 잔액을 확인해주세요 !```**'
            ), view=None)

bot.run(token)
