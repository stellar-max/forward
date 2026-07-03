from pyrogram import filters
from core.clients import bot
@bot.on_message(filters.command("spam"))
async def spam(_,m):await m.reply_text("Mass-send task center is present but protected. Use scheduler/publish flows; unsafe flood spam is intentionally not implemented.")
