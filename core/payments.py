from config import SUPPORT_ID,PAYMENT_TEXT
PLANS={"free":{"price":0,"text":"Free: 2 tasks, basic filters"},"premium":{"price":499,"text":"Premium: unlimited tasks, clone, edit/delete sync"},"business":{"price":1499,"text":"Business: heavy forwarding, priority support"},"lifetime":{"price":2999,"text":"Lifetime: one-time access"}}
def upgrade_text():
    rows=["💎 Upgrade Plans\n"]
    for k,v in PLANS.items():rows.append(f"{k.title()} — ₹{v['price']}\n{v['text']}")
    rows.append(f"\nPayment:\n{PAYMENT_TEXT}\n\nAfter payment, contact {SUPPORT_ID} with screenshot/user ID.")
    return "\n\n".join(rows)
