from utils.checks import parse_ids
def split_task_line(text):
    body=(text or '').split(maxsplit=1)
    if len(body)<2 or '->' not in body[1]:return [],[]
    left,right=body[1].split('->',1)
    return parse_ids(left),parse_ids(right)
def csv_items(text):return [x.strip() for x in (text or '').split(',') if x.strip()]
def arg(text,n=1):
    p=(text or '').split(maxsplit=n)
    return p[1:] if len(p)>1 else []
  
