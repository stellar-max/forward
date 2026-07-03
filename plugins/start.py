from pyrogram import filters,enums
from core.clients import bot
from core.database import db
from core.formatter import menu_text,guide_text
from utils.buttons import start_buttons
@bot.on_message(filters.command('start'))
async def start(_,m):
    if await db.is_gbanned(m.from_user.id):return await m.reply_text('You are globally banned from using this bot.')
    u=await db.upsert_user(m.from_user)
    await m.reply_text(menu_text(u),reply_markup=start_buttons(),disable_web_page_preview=True,parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('help'))
async def help_cmd(_,m):await m.reply_text(guide_text(),parse_mode=enums.ParseMode.HTML)
@bot.on_callback_query(filters.regex('^start$'))
async def start_cb(_,q):
    u=await db.upsert_user(q.from_user)
    await q.message.edit_text(menu_text(u),reply_markup=start_buttons(),disable_web_page_preview=True,parse_mode=enums.ParseMode.HTML)
