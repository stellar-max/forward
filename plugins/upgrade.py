from pyrogram import filters
from core.clients import bot
from core.payments import upgrade_text,PLANS
from core.database import db
from config import SUPPORT_ID
from utils.buttons import upgrade_buttons
@bot.on_message(filters.command("upgrade"))
async def upgrade(_,m):await m.reply_text(upgrade_text(),reply_markup=upgrade_buttons())
@bot.on_callback_query(filters.regex("^plan:"))
async def plan(_,q):
    plan=q.data.split(":",1)[1];p=PLANS.get(plan)
    if not p:return await q.answer("Invalid plan",show_alert=True)
    await db.create_payment(q.from_user.id,plan,"manual",p["price"],SUPPORT_ID)
    await q.message.edit_text(f"✅ Payment request created for {plan.title()}\n\nPay as shown in /upgrade, then contact {SUPPORT_ID} with screenshot and your user ID.")
@bot.on_message(filters.command("make_money"))
async def make_money(_,m):await m.reply_text("💰 Referral system placeholder: share your bot referral link and earn manual credits after admin verification.")
@bot.on_message(filters.command("get_app"))
async def get_app(_,m):await m.reply_text("📱 App links are not configured yet. Use this bot directly for now.")
