import telebot
from telebot.types import ChatPermissions
import datetime
from datetime import timedelta
token = 'TOKEN'
bot = telebot.TeleBot(token)
warnings = {}


def is_admin(msg):
    user = bot.get_chat_member(msg.chat.id,msg.from_user.id)
    return user.status in [ "administrator","creator"]

def add_warnings(chat_id,user_id):
    key = (chat_id,user_id)
    if key not in warnings:
        warnings[key] =0
    warnings[key]+=1
    return warnings[key]    
    

@bot.message_handler(func=lambda msg :(
    msg.text is not None and not  msg.text.startswith("/")
    
))
def anti_link(msg):
    if is_admin(msg):
        return    
    text = msg.text.lower()
    link_words = [
        "http://",
        "https://",
        "www.",
        "t.me/",
        "telegram.me/"
    ]
    has_link = any(link in text
                   for link in link_words)
    if not has_link:
        return
    try:
        bot.delete_message(msg.chat.id,msg.message_id)

    except Exception:
        pass     
    warnings_count = add_warnings(msg.chat.id,msg.from_user.id)
    if warnings_count <3:
        bot.send_message(msg.chat.id,f"""
    🔗 لینک ممنوع است.
    👤 کاربر:
        {msg.from_user.first_name}

        ⚠️ Warning:
        {warnings_count}/3 """
    )
    else:
        until_date  =(
            datetime.datetime.now()+timedelta(minutes=10)
        )
        try:
            bot.restrict_chat_member(msg.chat.id,msg.from_user.id,permissions=ChatPermissions(can_send_messages=False,can_send_other_messages=False),until_date=until_date)
            warnings[msg.chat.id,msg.from_user.id]=0            
        except ValueError as e:
            bot.reply_to(msg,"عملیات انجام نشد")    
        
        
        
        
    