import asyncio,time,uuid
from cachetools import TTLCache
from config import CACHE_TTL
TASK_CACHE={}
USER_CLIENTS={}
TASK_LOCKS={}
USER_LOCKS={}
DEDUP_CACHE=TTLCache(maxsize=200000,ttl=CACHE_TTL)
LIVE_EDIT_CACHE=TTLCache(maxsize=100000,ttl=30)
def now():return int(time.time())
def lock_for(pool,key):
    if key not in pool:pool[key]=asyncio.Lock()
    return pool[key]
def dedup_key(task_id,chat_id,msg_id):return f"{task_id}:{chat_id}:{msg_id}"
def new_id(prefix,uid):return f"{prefix}{uid}_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
