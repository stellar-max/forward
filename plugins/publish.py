from pyrogram import filters
from core.clients import bot
@bot.on_message(filters.command("publish"))
async def publish(_,m):await m.reply_text("Publish Center\n\nReview Publish tasks that already exist. Publish setup needs a task-specific configuration flow, which is not available from this screen yet; this page will not create, edit, or publish anything.\n\nShowing: All\n\nNo Publish tasks found for this view.")
