from utils.text import apply_replace,clean_text,has_any
async def transform_message(message,rules,task):
    text=(message.text or message.caption or "") if message else ""
    for r in rules:
        t=r.get("type")
        if t=="whitelist" and not has_any(text,r.get("items",[]),r.get("match_case",False)):return None,"whitelist"
        if t=="blacklist_skip" and has_any(text,r.get("items",[]),r.get("match_case",False)):return None,"blacklist"
    for r in rules:
        if r.get("type")=="blacklist_remove":
            for item in r.get("items",[]):text=text.replace(item,"")
        elif r.get("type") in ("replace","link_replace","username_replace"):text=apply_replace(text,r)
    cleaners={r.get("type"):r for r in rules if r.get("type","" ).startswith("clean_")}
    text=clean_text(text,remove_links=task.get("clean_links") or "clean_links" in cleaners,remove_usernames="clean_usernames" in cleaners,remove_hashtags="clean_hashtags" in cleaners,remove_emojis="clean_emojis" in cleaners)
    heads=[r.get("text","") for r in rules if r.get("type")=="header" and r.get("text")]
    foots=[r.get("text","") for r in rules if r.get("type")=="footer" and r.get("text")]
    if heads:text="\n".join(heads+[text]).strip()
    if foots:text="\n".join([text]+foots).strip()
    return text,None
