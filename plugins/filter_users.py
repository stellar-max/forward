from pyrogram import filters
from core.clients import bot
@bot.on_message(filters.command("filter_users"))
async def filter_users(_,m):await m.reply_text("Sender allow/block list UI placeholder. DB core is ready; add user IDs as task rules in next flow.")
