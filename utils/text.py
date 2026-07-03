import re

URL_RE=re.compile(r"https?://\S+|t\.me/\S+",re.I)
USER_RE=re.compile(r"(?<!\w)@[A-Za-z0-9_]{5,32}")
SPACE_RE=re.compile(r"[ \t]+")
EMOJI_RE=re.compile("[\U00010000-\U0010ffff]",flags=re.UNICODE)

def clean_text(text,remove_links=False,remove_usernames=False,remove_hashtags=False,remove_emojis=False):
    if not text:return text
    if remove_links:text=URL_RE.sub("",text)
    if remove_usernames:text=USER_RE.sub("",text)
    if remove_hashtags:text=re.sub(r"(?<!\w)#\w+","",text)
    if remove_emojis:text=EMOJI_RE.sub("",text)
    text="\n".join(SPACE_RE.sub(" ",x).strip() for x in text.splitlines())
    return re.sub(r"\n{3,}","\n\n",text).strip()
def apply_replace(text,rule):
    if not text:return text
    old=rule.get("from","");new=rule.get("to","")
    if not old:return text
    if rule.get("regex"):
        flags=0 if rule.get("match_case") else re.I
        return re.sub(old,new,text,flags=flags)
    return text.replace(old,new) if rule.get("match_case") else re.sub(re.escape(old),lambda _:new,text,flags=re.I)
def has_any(text,items,case=False):
    if not items:return False
    hay=text or "";hay2=hay if case else hay.lower()
    for i in items:
        n=str(i if case else str(i).lower())
        if n in hay2:return True
    return False
  
