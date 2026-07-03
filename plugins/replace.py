from pyrogram import filters
from core.clients import bot
from core.database import db
@bot.on_message(filters.command("replace"))
async def replace(_,m):
    p=(m.text or "").split(maxsplit=3)
    if len(p)<4:return await m.reply_text("Usage: /replace task_id old_text new_text")
    await db.add_rule(m.from_user.id,p[1],"replace",**{"from":p[2],"to":p[3],"match_case":False,"regex":False})
    await m.reply_text("✅ Replace rule added")
@bot.on_message(filters.command("replace_regex"))
async def replace_regex(_,m):
    p=(m.text or "").split(maxsplit=3)
    if len(p)<4:return await m.reply_text("Usage: /replace_regex task_id pattern replacement")
    await db.add_rule(m.from_user.id,p[1],"replace",**{"from":p[2],"to":p[3],"match_case":False,"regex":True})
    await m.reply_text("✅ Regex replace rule added")
