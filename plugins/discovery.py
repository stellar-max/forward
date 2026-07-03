from pyrogram import filters
from core.clients import bot
async def list_dialogs(client,kind,limit=50):
    rows=[]
    async for d in client.get_dialogs(limit=limit):
        c=d.chat;t=getattr(c,"type",None);name=getattr(t,"name",str(t)).lower()
        if kind=="channel" and "channel" not in name:continue
        if kind=="group" and "group" not in name and "supergroup" not in name:continue
        if kind=="user" and "private" not in name:continue
        if kind=="bot" and not getattr(c,"is_bot",False):continue
        rows.append(f"{c.title or c.first_name or c.username} — `{c.id}`")
    return rows or ["No chats found from active bot session. Use connected user session for full discovery."]
@bot.on_message(filters.command("getchannel"))
async def getchannel(c,m):await m.reply_text("📢 Channels\n\n"+"\n".join(await list_dialogs(c,"channel")))
@bot.on_message(filters.command("getgroup"))
async def getgroup(c,m):await m.reply_text("👥 Groups\n\n"+"\n".join(await list_dialogs(c,"group")))
@bot.on_message(filters.command("getuser"))
async def getuser(c,m):await m.reply_text("👤 Private Chats\n\n"+"\n".join(await list_dialogs(c,"user")))
@bot.on_message(filters.command("getbot"))
async def getbot(c,m):await m.reply_text("🤖 Bots\n\n"+"\n".join(await list_dialogs(c,"bot")))
