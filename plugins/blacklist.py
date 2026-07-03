from pyrogram import filters
from core.clients import bot
from core.database import db
@bot.on_message(filters.command("blacklist"))
async def blacklist(_,m):
    p=(m.text or "").split(maxsplit=3)
    if len(p)<4:return await m.reply_text("Usage: /blacklist task_id skip|remove word1,word2")
    mode="blacklist_skip" if p[2].lower()=="skip" else "blacklist_remove"
    items=[x.strip() for x in p[3].split(",") if x.strip()]
    await db.add_rule(m.from_user.id,p[1],mode,items=items,match_case=False)
    await m.reply_text("✅ Blacklist rule added")
