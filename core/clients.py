import os
from pyrogram import Client,filters
from pyrogram.handlers import MessageHandler,EditedMessageHandler,RawUpdateHandler
from config import API_ID,API_HASH,BOT_TOKEN,SESSION_DIR
from core.state import USER_CLIENTS,lock_for,USER_LOCKS
os.makedirs(SESSION_DIR,exist_ok=True)
bot=Client(os.path.join(SESSION_DIR,"bot"),api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN,plugins=dict(root="plugins"))
def _attach_forward_handlers(c):
    from core.forwarder import handle_incoming,handle_edit,handle_raw_delete
    async def _raw(cl,update,users,chats):await handle_raw_delete(cl,update)
    c.add_handler(MessageHandler(handle_incoming,filters.all & ~filters.service))
    c.add_handler(EditedMessageHandler(handle_edit,filters.all))
    c.add_handler(RawUpdateHandler(_raw))
async def get_user_client(uid):
    if uid in USER_CLIENTS:return USER_CLIENTS[uid]
    async with lock_for(USER_LOCKS,uid):
        if uid in USER_CLIENTS:return USER_CLIENTS[uid]
        c=Client(os.path.join(SESSION_DIR,f"user_{uid}"),api_id=API_ID,api_hash=API_HASH)
        _attach_forward_handlers(c);await c.start();USER_CLIENTS[uid]=c;return c
async def stop_user_client(uid):
    c=USER_CLIENTS.pop(uid,None)
    if c:await c.stop()
async def start_saved_sessions():
    from core.database import db
    for s in await db.sessions_list():
        if not s.get('active',True):continue
        uid=s.get('user_id')
        path=os.path.join(SESSION_DIR,f'user_{uid}.session')
        if not os.path.exists(path):continue
        try:await get_user_client(uid)
        except Exception as e:print(f"⚠️ Could not start saved session for {uid}: {e}")
async def stop_all_user_clients():
    for uid in list(USER_CLIENTS.keys()):
        try:await stop_user_client(uid)
        except Exception:pass
