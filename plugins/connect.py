import os,shutil
from pyrogram import filters,enums
from core.clients import bot,stop_user_client
from core.database import db
from config import SESSION_DIR,OWNER_ID
from utils.checks import owner_only
@bot.on_message(filters.command('connect'))
async def connect(_,m):
    await db.set_connected(m.from_user.id,True)
    await m.reply_text('✅ Account connect flag enabled.\n\nFor real userbot login, put the Pyrogram session file as sessions/user_<your_id>.session, then restart. This avoids unsafe OTP collection inside chat.')
@bot.on_message(filters.command('disconnect'))
async def disconnect(_,m):
    await stop_user_client(m.from_user.id);await db.set_session_active(m.from_user.id,False)
    await m.reply_text('✅ Disconnected from active user session.')
@bot.on_message(filters.command('sessions'))
async def sessions(_,m):
    if not await owner_only(m):return
    rows=await db.sessions_list()
    if not rows:return await m.reply_text('No sessions saved.')
    body='\n'.join(f'{x["user_id"]} | active={x.get("active",True)} | {x.get("path","")}' for x in rows[:100])
    body=body.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    await m.reply_text('<b>🔐 Sessions</b>\n<blockquote expandable>'+body+'</blockquote>',parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('session_status'))
async def session_status(_,m):
    if not await owner_only(m):return
    p=(m.text or '').split(maxsplit=1)
    if len(p)<2:return await m.reply_text('Usage: /session_status user_id')
    try:uid=int(p[1])
    except Exception:return await m.reply_text('Invalid user ID')
    s=await db.session(uid);path=os.path.join(SESSION_DIR,f'user_{uid}.session')
    exists=os.path.exists(path)
    await m.reply_text(f'<b>Session Status</b>\n<blockquote expandable>User: {uid}\nDB: {bool(s)}\nFile: {exists}\nPath: {path}</blockquote>',parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('session_delete'))
async def session_delete(_,m):
    if not await owner_only(m):return
    p=(m.text or '').split(maxsplit=1)
    if len(p)<2:return await m.reply_text('Usage: /session_delete user_id')
    try:uid=int(p[1])
    except Exception:return await m.reply_text('Invalid user ID')
    await stop_user_client(uid);await db.delete_session(uid)
    for ext in ('.session','.session-journal'):
        path=os.path.join(SESSION_DIR,f'user_{uid}{ext}')
        if os.path.exists(path):os.remove(path)
    await m.reply_text(f'✅ Session deleted for {uid}')
@bot.on_message(filters.command('session_add'))
async def session_add(_,m):
    if not await owner_only(m):return
    p=(m.text or '').split(maxsplit=1)
    if len(p)<2 or not m.reply_to_message or not m.reply_to_message.document:return await m.reply_text('Usage: reply to a .session file with /session_add user_id')
    try:uid=int(p[1])
    except Exception:return await m.reply_text('Invalid user ID')
    os.makedirs(SESSION_DIR,exist_ok=True);tmp=await m.reply_to_message.download()
    dest=os.path.join(SESSION_DIR,f'user_{uid}.session');shutil.move(tmp,dest)
    await db.save_session(uid,dest,m.from_user.id);await m.reply_text(f'✅ Session file added for {uid}')
@bot.on_message(filters.command('get_session'))
async def get_session(_,m):
    if not await owner_only(m):return
    p=(m.text or '').split(maxsplit=1)
    if len(p)<2:return await m.reply_text('Usage: /get_session user_id')
    try:uid=int(p[1])
    except Exception:return await m.reply_text('Invalid user ID')
    if uid!=int(OWNER_ID):return await m.reply_text('For safety, this bot will not export another user\'s Telegram session. Use /session_status or /session_delete instead.')
    path=os.path.join(SESSION_DIR,f'user_{uid}.session')
    if not os.path.exists(path):return await m.reply_text('Owner session file not found.')
    await m.reply_document(path,caption='Owner session export.')
@bot.on_callback_query(filters.regex('^connect$'))
async def connect_cb(_,q):await q.message.edit_text('Use /connect. For safe login, generate a Pyrogram user session locally and place it inside sessions/user_<id>.session.')
@bot.on_callback_query(filters.regex('^support$'))
async def support_cb(_,q):
    from config import SUPPORT_ID
    await q.answer(SUPPORT_ID,show_alert=True)
