from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
def start_buttons():return InlineKeyboardMarkup([[InlineKeyboardButton("Connect Now",callback_data="connect")],[InlineKeyboardButton("Support",callback_data="support")]])
def back_btn(to="start"):return InlineKeyboardMarkup([[InlineKeyboardButton("Back",callback_data=to)]])
def upgrade_buttons():return InlineKeyboardMarkup([[InlineKeyboardButton("Premium",callback_data="plan:premium"),InlineKeyboardButton("Business",callback_data="plan:business")],[InlineKeyboardButton("Lifetime",callback_data="plan:lifetime")],[InlineKeyboardButton("Contact Support",callback_data="support")]])
  
