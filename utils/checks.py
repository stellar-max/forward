from config import OWNER_ID
def is_owner(uid):return int(uid or 0)==int(OWNER_ID)
def parse_ids(text):
    ids=[]
    for p in (text or '').replace(',', ' ').split():
        try:ids.append(int(p))
        except Exception:pass
    return ids
async def owner_only(m):
    if not m.from_user or not is_owner(m.from_user.id):
        await m.reply_text('Owner only command.');return False
    return True
  
