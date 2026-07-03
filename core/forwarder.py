import asyncio
from pyrogram.errors import FloodWait,RPCError
from pyrogram.raw.types import UpdateDeleteMessages,UpdateDeleteChannelMessages
from core.database import db
from core.filters import transform_message
from core.scheduler import sleep_delay
from core.state import DEDUP_CACHE,dedup_key,lock_for,TASK_LOCKS
async def send_copy(client,message,target,text,task,reply_to=None):
    kwargs={'reply_to_message_id':reply_to,'disable_notification':True}
    if message.text:return await client.send_message(target,text or message.text,disable_web_page_preview=task.get('clear_url_preview',True),**kwargs)
    if message.caption is not None and text!=message.caption:
        if message.photo:return await client.send_photo(target,message.photo.file_id,caption=text,**kwargs)
        if message.video:return await client.send_video(target,message.video.file_id,caption=text,**kwargs)
        if message.document:
            if task.get('clean_documents'):return None
            return await client.send_document(target,message.document.file_id,caption=text,**kwargs)
    if message.document and task.get('clean_documents'):return None
    return await client.copy_message(target,message.chat.id,message.id,caption=text if text else None,reply_to_message_id=reply_to)
async def forward_message(client,message,task):
    if await db.is_gbanned(task.get('owner_id')):return
    key=dedup_key(task['_id'],message.chat.id,message.id)
    if key in DEDUP_CACHE:return
    DEDUP_CACHE[key]=1
    async with lock_for(TASK_LOCKS,task['_id']):
        rules=await db.rules_for_task(task['_id']);text,blocked=await transform_message(message,rules,task)
        if blocked:return
        await sleep_delay(task.get('delay_seconds',0))
        for target in task.get('targets',[]):
            reply_to=None
            if task.get('sync_replies') and message.reply_to_message:
                maps=await db.maps_for_source(task['_id'],message.chat.id,message.reply_to_message.id)
                for mp in maps:
                    if int(mp['target_chat_id'])==int(target):reply_to=mp['target_msg_id'];break
            try:
                sent=await client.forward_messages(target,message.chat.id,message.id) if task.get('show_forward_header') and not task.get('copy_mode') else await send_copy(client,message,target,text,task,reply_to)
                if sent:await db.save_map(task['_id'],message.chat.id,message.id,target,sent.id)
            except FloodWait as e:await asyncio.sleep(int(e.value)+1)
            except RPCError:continue
async def handle_incoming(client,message):
    if not message or not message.chat:return
    tasks=await db.active_tasks_for_source(message.chat.id)
    for task in tasks:await forward_message(client,message,task)
async def handle_edit(client,message):
    if not message or not message.chat:return
    maps=await db.maps_by_source_msg(message.chat.id,message.id)
    if not maps:return
    grouped={}
    for mp in maps:grouped.setdefault(mp['task_id'],[]).append(mp)
    for tid,items in grouped.items():
        task=await db.get_task(tid)
        if not task or not task.get('sync_edits',True) or await db.is_gbanned(task.get('owner_id')):continue
        rules=await db.rules_for_task(tid);text,blocked=await transform_message(message,rules,task)
        if blocked:continue
        for mp in items:
            try:
                if message.text:await client.edit_message_text(mp['target_chat_id'],mp['target_msg_id'],text,disable_web_page_preview=task.get('clear_url_preview',True))
                elif message.caption is not None:await client.edit_message_caption(mp['target_chat_id'],mp['target_msg_id'],text)
            except RPCError:continue
async def handle_raw_delete(client,update):
    if isinstance(update,UpdateDeleteMessages):return
    if isinstance(update,UpdateDeleteChannelMessages):chat_id=int(f'-100{update.channel_id}');ids=list(update.messages)
    else:return
    for mid in ids:
        maps=await db.maps_by_source_msg(chat_id,mid)
        for mp in maps:
            task=await db.get_task(mp['task_id'])
            if task and task.get('sync_deletes',True):
                try:await client.delete_messages(mp['target_chat_id'],mp['target_msg_id'])
                except RPCError:pass
    await db.delete_maps_for_source(chat_id,ids)
