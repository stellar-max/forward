from pyrogram import filters,enums
from core.clients import bot
from core.database import db
from core.forwarder import handle_incoming,handle_edit,handle_raw_delete
from core.formatter import preview_task
from utils.parser import split_task_line
@bot.on_message(filters.command('forward'))
async def forward_cmd(_,m):
    uid=m.from_user.id;sources,targets=split_task_line(m.text)
    if not sources and not targets:
        tasks=await db.owner_tasks(uid)
        text='<b>📨 Forward Tasks</b>\n\n'+('\n'.join(preview_task(t) for t in tasks) if tasks else '<blockquote expandable>No tasks found.\n\nCreate one:\n/forward -100111 -> -100222</blockquote>')
        return await m.reply_text(text,parse_mode=enums.ParseMode.HTML)
    if not sources or not targets:return await m.reply_text('Usage:\n/forward source1 source2 -> target1 target2')
    try:t=await db.create_task(uid,sources,targets)
    except PermissionError as e:return await m.reply_text(str(e))
    await m.reply_text('✅ <b>Forward task created</b>\n'+preview_task(t),parse_mode=enums.ParseMode.HTML)
@bot.on_message(filters.command('task_on'))
async def task_on(_,m):
    p=(m.text or '').split(maxsplit=1)
    if len(p)<2:return await m.reply_text('Usage: /task_on task_id')
    t=await db.update_task(p[1],m.from_user.id,enabled=True);await m.reply_text('✅ Enabled' if t else 'Task not found')
@bot.on_message(filters.command('task_off'))
async def task_off(_,m):
    p=(m.text or '').split(maxsplit=1)
    if len(p)<2:return await m.reply_text('Usage: /task_off task_id')
    t=await db.update_task(p[1],m.from_user.id,enabled=False);await m.reply_text('⏸ Disabled' if t else 'Task not found')
@bot.on_message(filters.command('header'))
async def header(_,m):
    p=(m.text or '').split(maxsplit=2)
    if len(p)<3:return await m.reply_text('Usage: /header task_id text')
    await db.add_rule(m.from_user.id,p[1],'header',text=p[2]);await m.reply_text('✅ Header added')
@bot.on_message(filters.command('footer'))
async def footer(_,m):
    p=(m.text or '').split(maxsplit=2)
    if len(p)<3:return await m.reply_text('Usage: /footer task_id text')
    await db.add_rule(m.from_user.id,p[1],'footer',text=p[2]);await m.reply_text('✅ Footer added')
@bot.on_message(filters.command('delay'))
async def delay(_,m):
    p=(m.text or '').split(maxsplit=2)
    if len(p)<3:return await m.reply_text('Usage: /delay task_id seconds')
    try:s=max(0,int(p[2]))
    except Exception:return await m.reply_text('Seconds must be number')
    await db.update_task(p[1],m.from_user.id,delay_seconds=s);await m.reply_text(f'✅ Delay set to {s}s')
@bot.on_message(filters.command('forward_header'))
async def fheader(_,m):
    p=(m.text or '').split(maxsplit=2)
    if len(p)<3 or p[2].lower() not in ('on','off'):return await m.reply_text('Usage: /forward_header task_id on|off')
    on=p[2].lower()=='on';await db.update_task(p[1],m.from_user.id,show_forward_header=on,copy_mode=not on);await m.reply_text('✅ Forward header ON' if on else '✅ Forward header OFF')
@bot.on_edited_message(filters.all)
async def edited(c,m):await handle_edit(c,m)
@bot.on_raw_update()
async def raw(c,update,users,chats):await handle_raw_delete(c,update)
@bot.on_message(filters.all & ~filters.service & ~filters.command(['start','help','forward','task_on','task_off','header','footer','delay','forward_header','replace','replace_regex','whitelist','blacklist','filter_users','getchannel','getgroup','getuser','getbot','profile','settings','language','upgrade','make_money','get_app','connect','disconnect','clone','publish','spam','restart','gban','ungban','gbanlist','sessions','session_status','session_delete','session_add','get_session']))
async def incoming(c,m):await handle_incoming(c,m)
