from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING,DESCENDING
from config import MONGO_URL,DB_NAME,MAX_FREE_TASKS,MAX_FREE_RULES,DEFAULT_LANG
from core.state import now,new_id
class Database:
    def __init__(self):
        self.client=AsyncIOMotorClient(MONGO_URL);self.db=self.client[DB_NAME]
        self.users=self.db.users;self.tasks=self.db.tasks;self.rules=self.db.rules;self.maps=self.db.message_map;self.payments=self.db.payments;self.sessions=self.db.sessions;self.gbans=self.db.gbans
    async def setup(self):
        await self.users.create_index([('status',ASCENDING)])
        await self.tasks.create_index([('owner_id',ASCENDING),('enabled',ASCENDING)])
        await self.tasks.create_index([('sources',ASCENDING)])
        await self.rules.create_index([('task_id',ASCENDING),('enabled',ASCENDING),('type',ASCENDING)])
        await self.maps.create_index([('task_id',ASCENDING),('source_chat_id',ASCENDING),('source_msg_id',ASCENDING)])
        await self.maps.create_index([('target_chat_id',ASCENDING),('target_msg_id',ASCENDING)])
        await self.payments.create_index([('user_id',ASCENDING),('created_at',DESCENDING)])
        await self.sessions.create_index([('user_id',ASCENDING)],unique=True)
        await self.gbans.create_index([('created_at',DESCENDING)])
    async def upsert_user(self,user):
        uid=user.id;doc={'_id':uid,'name':getattr(user,'first_name','') or 'User','username':getattr(user,'username',None),'updated_at':now()}
        await self.users.update_one({'_id':uid},{'$set':doc,'$setOnInsert':{'plan':'free','status':'active','language':DEFAULT_LANG,'connected':False,'session_name':f'user_{uid}','created_at':now()}},upsert=True)
        return await self.users.find_one({'_id':uid})
    async def user(self,uid):return await self.users.find_one({'_id':int(uid)})
    async def set_connected(self,uid,connected):return await self.users.update_one({'_id':int(uid)},{'$set':{'connected':bool(connected),'updated_at':now()},'$setOnInsert':{'name':'User','username':None,'plan':'free','status':'active','language':DEFAULT_LANG,'session_name':f'user_{uid}','created_at':now()}},upsert=True)
    async def can_add_task(self,uid):
        u=await self.user(uid) or {};return True if u.get('plan','free')!='free' else await self.tasks.count_documents({'owner_id':int(uid)})<MAX_FREE_TASKS
    async def create_task(self,uid,sources,targets,**opts):
        if await self.is_gbanned(uid):raise PermissionError('You are globally banned from using this bot.')
        if not await self.can_add_task(uid):raise PermissionError('Free task limit reached. Upgrade to create more forwarding tasks.')
        tid=new_id('t',uid);doc={'_id':tid,'owner_id':int(uid),'enabled':True,'sources':list(dict.fromkeys(map(int,sources))),'targets':list(dict.fromkeys(map(int,targets))),'copy_mode':True,'show_forward_header':False,'clean_links':False,'clear_url_preview':True,'clean_documents':False,'premium_copy':True,'sync_edits':True,'sync_deletes':True,'sync_replies':True,'delay_seconds':0,'schedule':None,'active_hours':{'enabled':False,'start':'00:00','end':'23:59','timezone':'Asia/Kolkata'},'created_at':now(),'updated_at':now()}
        doc.update(opts);await self.tasks.insert_one(doc);return doc
    async def update_task(self,tid,uid=None,**data):
        q={'_id':tid};
        if uid is not None:q['owner_id']=int(uid)
        data['updated_at']=now();await self.tasks.update_one(q,{'$set':data});return await self.tasks.find_one(q)
    async def get_task(self,tid,uid=None):
        q={'_id':tid};
        if uid is not None:q['owner_id']=int(uid)
        return await self.tasks.find_one(q)
    async def active_tasks_for_source(self,chat_id):return await self.tasks.find({'sources':int(chat_id),'enabled':True}).to_list(None)
    async def owner_tasks(self,uid):return await self.tasks.find({'owner_id':int(uid)}).sort('created_at',-1).to_list(None)
    async def add_rule(self,uid,task_id,rtype,**data):
        if await self.is_gbanned(uid):raise PermissionError('You are globally banned from using this bot.')
        if (await self.user(uid) or {}).get('plan','free')=='free' and await self.rules.count_documents({'owner_id':int(uid)})>=MAX_FREE_RULES:raise PermissionError('Free rule limit reached. Upgrade to add more rules.')
        rid=new_id('r',uid);doc={'_id':rid,'owner_id':int(uid),'task_id':task_id,'type':rtype,'enabled':True,'created_at':now()};doc.update(data);await self.rules.insert_one(doc);return doc
    async def rules_for_task(self,task_id):return await self.rules.find({'task_id':task_id,'enabled':True}).sort('created_at',1).to_list(None)
    async def save_map(self,task_id,src_chat,src_msg,tgt_chat,tgt_msg):
        key=f'{task_id}:{src_chat}:{src_msg}:{tgt_chat}';doc={'_id':key,'task_id':task_id,'source_chat_id':int(src_chat),'source_msg_id':int(src_msg),'target_chat_id':int(tgt_chat),'target_msg_id':int(tgt_msg),'created_at':now()}
        await self.maps.update_one({'_id':key},{'$set':doc},upsert=True);return doc
    async def maps_for_source(self,task_id,src_chat,src_msg):return await self.maps.find({'task_id':task_id,'source_chat_id':int(src_chat),'source_msg_id':int(src_msg)}).to_list(None)
    async def maps_by_source_msg(self,src_chat,src_msg):return await self.maps.find({'source_chat_id':int(src_chat),'source_msg_id':int(src_msg)}).to_list(None)
    async def delete_maps_for_source(self,src_chat,msg_ids):return await self.maps.delete_many({'source_chat_id':int(src_chat),'source_msg_id':{'$in':list(map(int,msg_ids))}})
    async def create_payment(self,uid,plan,method,amount,contact):
        pid=new_id('p',uid);doc={'_id':pid,'user_id':int(uid),'plan':plan,'status':'pending','method':method,'amount':amount,'contact':contact,'created_at':now()};await self.payments.insert_one(doc);return doc
    async def save_session(self,uid,path,by=None):
        doc={'_id':int(uid),'user_id':int(uid),'path':path,'active':True,'updated_at':now(),'added_by':by}
        await self.sessions.update_one({'_id':int(uid)},{'$set':doc,'$setOnInsert':{'created_at':now()}},upsert=True);await self.set_connected(uid,True);return doc
    async def session(self,uid):return await self.sessions.find_one({'_id':int(uid)})
    async def sessions_list(self):return await self.sessions.find({}).sort('updated_at',-1).to_list(100)
    async def delete_session(self,uid):
        await self.sessions.delete_one({'_id':int(uid)});await self.set_connected(uid,False)
    async def set_session_active(self,uid,active):
        await self.sessions.update_one({'_id':int(uid)},{'$set':{'active':bool(active),'updated_at':now()}});await self.set_connected(uid,active)
    async def gban(self,uid,reason='',by=0):
        doc={'_id':int(uid),'user_id':int(uid),'reason':reason or 'No reason','by':int(by or 0),'created_at':now()}
        await self.gbans.update_one({'_id':int(uid)},{'$set':doc},upsert=True);return doc
    async def ungban(self,uid):return await self.gbans.delete_one({'_id':int(uid)})
    async def is_gbanned(self,uid):return await self.gbans.find_one({'_id':int(uid)}) is not None
    async def gbanlist(self):return await self.gbans.find({}).sort('created_at',-1).to_list(200)
db=Database()
