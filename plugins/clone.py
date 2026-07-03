import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait,RPCError
from core.clients import bot
from core.database import db
from utils.checks import parse_ids
from config import MAX_CLONE_LIMIT
@bot.on_message(filters.command("clone"))
async def clone(_,m):
    p=(m.text or "").split(maxsplit=3)
    if len(p)<4:return await m.reply_text("Usage: /clone source_chat_id target_chat_id limit")
    ids=parse_ids(" ".join(p[1:3]))
    if len(ids)<2:return await m.reply_text("Invalid source/target chat IDs")
    try:limit=min(max(1,int(p[3])),MAX_CLONE_LIMIT)
    except Exception:return await m.reply_text("Limit must be number")
    msg=await m.reply_text(f"📦 Clone started: {limit} messages")
    sent=0
    async for x in _.get_chat_history(ids[0],limit=limit):
        try:
            out=await _.copy_message(ids[1],ids[0],x.id)
            await db.save_map(f"clone_{m.from_user.id}",ids[0],x.id,ids[1],out.id);sent+=1
        except FloodWait as e:await asyncio.sleep(int(e.value)+1)
        except RPCError:continue
    await msg.edit_text(f"✅ Clone finished\nCopied: {sent}/{limit}")
