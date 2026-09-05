import telebot

bot = telebot.TeleBot("YOUR TOKEN")
def is_admin(msg):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    admins = bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return True
    return False


#================KICK====================

@bot.message_handler(commands=['kick'])
def kick_user(msg):
    if not is_admin(msg):
        bot.send_message(msg.chat.id,'just admin can kick a member')
        return

    if not msg.reply_to_message:
        bot.send_message(msg.chat.id,'please reply on the member message who you want to kick ')
        return
    user_id = msg.reply_to_message.from_user.id
    chat_id = msg.chat.id
    try:
        bot.ban_chat_member(chat_id,user_id)
        bot.unban_chat_member(chat_id,user_id,only_if_banned=True)
        bot.reply_to(msg,f'member {msg.reply_to_message.from_user.first_name} kicked from group')
    except Exception as e:
        bot.reply_to(msg,f'error\n{e}')


#=====================BAN====================
@bot.message_handler(commands=['ban'])
def ban_member(msg):

    if not is_admin(msg):
        bot.send_message(msg.chat.id, 'just admin can ban a member')
        return
    if not msg.reply_to_message:
        bot.send_message(msg.chat.id,'please reply on the member message who you want to kick ')
        return
    user_id = msg.reply_to_message.from_user.id
    chat_id = msg.chat.id
    try:
        bot.ban_chat_member(chat_id,user_id)
        bot.reply_to(msg,f'member {msg.reply_to_message.from_user.first_name} banned from group')
    except Exception as e:
        bot.reply_to(msg,f'error\n{e}')

@bot.message_handler(commands=['unban'])
def unban_member(msg):
    if not is_admin(msg):
        bot.send_message(msg.chat.id, 'just admin can ban a member')
        return

    if not msg.reply_to_message:
        bot.send_message(msg.chat.id,'please reply on the member message who you want to kick ')
        return
    user_id = msg.reply_to_message.from_user.id

    chat_id = msg.chat.id
    try:
        bot.unban_chat_member(chat_id,user_id)
        bot.reply_to(msg,f'member {msg.reply_to_message.from_user.first_name} unbanned from group')
    except Exception as e:
        bot.reply_to(msg,f'error\n{e}')

bot.infinity_polling()

