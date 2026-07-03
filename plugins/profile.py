from pyrogram import filters
from core.clients import bot
from core.database import db
@bot.on_message(filters.command("profile"))
async def profile(_,m):
    u=await db.upsert_user(m.from_user);tasks=await db.owner_tasks(m.from_user.id)
    await m.reply_text(f"👤 Profile\n\nID: {m.from_user.id}\nPlan: {u.get('plan','free')}\nConnected: {u.get('connected',False)}\nTasks: {len(tasks)}")
