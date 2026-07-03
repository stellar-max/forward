import os,sys
from pyrogram import filters,enums
from core.clients import bot
from core.database import db
from utils.checks import owner_only
@bot.on_message(filters.command('settings'))
async def settings(_,m):
    tasks=await db.owner_tasks(m.from_user.id)
    text='<b>⚙️ Settings</b>\n\n<blockquote expandable>Tasks: {}\nDefault language: English\n\nUse /forward, /replace, /blacklist, /whitelist, /delay, /forward_header.</blockquote>'.format(len(tasks))
    await m.reply_text(text,parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('language'))
async def language(_,m):await m.reply_text('<b>🌐 Language</b>\n\n<blockquote expandable>Default language is English. Multi-language core is ready; add more strings later.</blockquote>',parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('restart'))
async def restart(_,m):
    if not await owner_only(m):return
    await m.reply_text('♻️ Restarting...')
    os.execv(sys.executable,[sys.executable]+sys.argv)
@bot.on_message(filters.command('gban'))
async def gban(_,m):
    if not await owner_only(m):return
    p=(m.text or '').split(maxsplit=2)
    if len(p)<2:return await m.reply_text('Usage: /gban user_id reason')
    try:uid=int(p[1])
    except Exception:return await m.reply_text('Invalid user ID')
    if uid==m.from_user.id:return await m.reply_text('You cannot gban yourself.')
    doc=await db.gban(uid,p[2] if len(p)>2 else 'No reason',m.from_user.id)
    await m.reply_text(f'✅ Globally banned <code>{doc["user_id"]}</code>\nReason: {doc["reason"]}',parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('ungban'))
async def ungban(_,m):
    if not await owner_only(m):return
    p=(m.text or '').split(maxsplit=1)
    if len(p)<2:return await m.reply_text('Usage: /ungban user_id')
    try:uid=int(p[1])
    except Exception:return await m.reply_text('Invalid user ID')
    await db.ungban(uid);await m.reply_text(f'✅ Unbanned <code>{uid}</code>',parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('gbanlist'))
async def gbanlist(_,m):
    if not await owner_only(m):return
    rows=await db.gbanlist()
    if not rows:return await m.reply_text('GBan list is empty.')
    body='\n'.join(f'{x["user_id"]} — {x.get("reason","No reason")}' for x in rows[:100])
    await m.reply_text('<b>🛡 GBan List</b>\n<blockquote expandable>'+body.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')+'</blockquote>',parse_mode=enums.ParseMode.HTML)
