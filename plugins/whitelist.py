from pyrogram import filters
from core.clients import bot
from core.database import db
@bot.on_message(filters.command("whitelist"))
async def whitelist(_,m):
    p=(m.text or "").split(maxsplit=2)
    if len(p)<3:return await m.reply_text("Usage: /whitelist task_id word1,word2")
    items=[x.strip() for x in p[2].split(",") if x.strip()]
    await db.add_rule(m.from_user.id,p[1],"whitelist",items=items,match_case=False)
    await m.reply_text("✅ Whitelist rule added")
