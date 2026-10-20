import telebot
from telebot import types
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')


print(BOT_TOKEN)

bot = telebot.TeleBot(BOT_TOKEN)

carts = {}

products_data = [
    {
        "id": 1,
        "name": "iPhone 15",
        "price": 1200,
        "stock": 15
    },
    {
        "id": 2,
        "name": "MacBook Pro",
        "price": 2500,
        "stock": 8
    },
    {
        "id": 3,
        "name": "AirPods Pro",
        "price": 250,
        "stock": 20
    }
]

def get_product(product_id):
    for product in products_data:
        if product['id']==product_id:
            return product
    return None

def show_cart(chat_id,user_id,message_id=None):
    user_cart = carts.get(user_id,{})
    if not user_cart:
        text = '🛒 سبد خرید شما خالی است.'
        if message_id is not None:
            bot.edit_message_text(text,chat_id,message_id,)
        else:
            bot.send_message(chat_id,text)
        return
    
    text = "🛒 سبد خرید شما:\n\n"
    total_price = 0
    keyboard = types.InlineKeyboardMarkup()
    for product_id,quantity in user_cart.items():
        product = get_product(product_id) 
        if product is not None:
            continue
        item_total = product['price']*quantity   
        total_price +=item_total
        text += (
            f"📦 {product['name']}\n"
            f"🔢 تعداد: {quantity}\n"
            f"💰 قیمت: ${item_total}\n\n"
        )
        
        keyboard.row(
            types.InlineKeyboardButton(
                "➕",
                callback_data=f"cart:increase:{product_id}"
            ),
            types.InlineKeyboardButton(
                "➖",
                callback_data=f"cart:decrease:{product_id}"
            ),
            types.InlineKeyboardButton(
                "🗑️",
                callback_data=f"cart:remove:{product_id}"
            )
        )
        
        text += "━━━━━━━━━━━━\n"
        text += f"💳 مجموع کل: ${total_price}"
        keyboard.row(types.InlineKeyboardButton("ثبت سفارش",callback_data=f'cart:checkout'))

        if message_id is not None:
            bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=keyboard
        )
        else:
         
            bot.send_message(
            chat_id,
            text,
            reply_markup=keyboard
        )
            
 


def main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        "🛍️ محصولات",
        "🛒 سبد خرید"
    )

    keyboard.row(
        "📦 سفارش‌های من",
        "👤 حساب کاربری"
    )
    return keyboard


@bot.message_handler(commands=['start'])
def welcome(msg):
    bot.send_message(
        msg.chat.id,
        "سلام 👋\n"
        "به فروشگاه ما خوش آمدید 🛍️",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda msg:msg.text=="🛍️ محصولات")
def products(msg):
    keyboard = types.InlineKeyboardMarkup()
    for product in products_data:
        btn = types.InlineKeyboardButton(text=f"{product['name']} - ${product['price']}",callback_data=f'product:{product["id"]}')
        
        keyboard.add(btn)
        
    bot.send_message(
        msg.chat.id,
        "🛍️ محصولات فروشگاه:",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda msg:msg.text=="🛒 سبد خرید")
def cart(msg):
    show_cart(
        chat_id=msg.chat.id,
        user_id=msg.from_user.id
    )

@bot.message_handler(func=lambda msg:msg.startswith("cart:increase:"))
def increase_cart_item (call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])


@bot.message_handler(func=lambda message: message.text == "📦 سفارش‌های من")
def orders(message):
    bot.send_message(
        message.chat.id,
        "📦 شما هنوز سفارشی ثبت نکرده‌اید."
    )

@bot.message_handler(func=lambda message: message.text == "👤 حساب کاربری")
def account(message):
    bot.send_message(
        message.chat.id,
        "👤 حساب کاربری\n\n"
        f"نام: {message.from_user.first_name}\n"
        f"شناسه کاربری: {message.from_user.id}"
    )

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("product:")
)
def product_callback(call):

    bot.answer_callback_query(call.id)

    product_id = int(call.data.split(":")[1])

    for product in products_data:

        if product["id"] == product_id:

            keyboard = types.InlineKeyboardMarkup()

            add_button = types.InlineKeyboardButton(
                text="🛒 افزودن به سبد",
                callback_data=f"cart:add:{product['id']}"
            )

            back_button = types.InlineKeyboardButton(
                text="🔙 بازگشت",
                callback_data="products"
            )

            keyboard.add(add_button)
            keyboard.add(back_button)

            bot.send_message(
                call.message.chat.id,
                f"📦 {product['name']}\n\n"
                f"💰 قیمت: ${product['price']}\n"
                f"📦 موجودی: {product['stock']} عدد",
                reply_markup=keyboard
            )

            break

@bot.callback_query_handler(func=lambda call:call.data.startswith("cart:add:"))
def add_to_cart_callback(call):
    product_id = int(call.data.split(":")[2])
    user_id = call.from_user.id
    if user_id not in carts:
        carts[user_id] = {}

    carts[user_id][product_id] =(
        carts[user_id].get(product_id,0)+1
    )
    bot.answer_callback_query(
        call.id,
        "✅ محصول به سبد خرید اضافه شد!"
    )
@bot.callback_query_handler(func= lambda call:call.data.startswith('products'))
def back_btn(call):
    bot.answer_callback_query(call.id)
    keyboard = types.InlineKeyboardMarkup()
    for product in products_data:
        button = types.InlineKeyboardButton(
            text=f"{product['name']} - ${product['price']}",
            callback_data=f"product:{product['id']}"
        )
        keyboard.add(button)



    bot.edit_message_text(
        "🛍️ محصولات فروشگاه:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )
    
    
@bot.callback_query_handler(func=lambda call:call.data.startswith('cart:increase:'))
def increase_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(':')[2])
    user_cart = carts.get(user_id,{})
    product  = get_product(product_id)
    if product is None or product_id not in user_cart:
        bot.answer_callback_query(call.id,"محصول در سبد خرید پیدا نشد.")
        return
    if user_cart[product_id] >=product['stock']:
        bot.answer_callback_query(call.id,"موجودی این محصول کافی نیست.")
        return 
    user_cart[product_id] +=1
    bot.answer_callback_query(call.id,"✅ تعداد محصول افزایش یافت.")
    show_cart(chat_id=call.message.chat.id,user_id=user_id,message_id=call.message.id)

@bot.callback_query_handler(func=lambda call:call.data.startswith('cart:decrease:'))
def decrease_product(call):    
    user_id = call.from_user.id
    product_id = int(call.data.split(':')[2])
    user_cart = carts.get(user_id,{})
    product = get_product(user_id)
    if product is None or product_id not in user_cart:
        bot.answer_callback_query(call.id,"محصول در سبد خرید پیدا نشد.")
        return
    if user_cart[product_id] <= 1:
        bot.answer_callback_query(call.id,"محصول نمیتواند صفر باشد")
        
        return    
    user_cart[product_id]-=1
    bot.answer_callback_query(call.id,"✅ تعداد محصول کاهش یافت.")
    show_cart(chat_id=call.message.chat.id,user_id=user_id,message_id=call.message.message_id)
@bot.callback_query_handler(func=lambda call : call.data.startswith("cart:remove:"))
def remove_product(call):
    user_id = call.from_user.id
    product_id = int(call.data.split(":")[2])
    product = get_product(product_id)
    user_cart = carts.get(user_id,{})
    if product is None or product_id not in user_cart:
        bot.answer_callback_query(call.id,"محصول در سبد خرید پیدا نشد.")
        return

    del user_cart[product_id]
    bot.answer_callback_query(call.id,'✅ محصول با موفقیت حذف شد ')
    show_cart(chat_id=call.message.chat.id,user_id=user_id,message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call : call.data.startswith("cart:checkout"))

def checkout(call):
    user_id = call.from_user.id
    user_cart = carts.get(user_id,{})
    if not user_cart  :
        bot.answer_callback_query(call.id,'سبد خرید خالی است ')
        return
    total_price = 0
    text = "🛍️ محصولات سفارش شما:\n\n"
    for product_id , quantity in user_cart.items():
        product = get_product(product_id)
        item_total = product["price"] * quantity
        total_price += item_total
        text += (
            f"📦 {product['name']}\n"
            f"🔢 تعداد: {quantity}\n"
            f"💰 قیمت این محصول: ${item_total}\n\n"
        )
    text += f"💳 مبلغ نهایی: ${total_price}"
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text)



print('bot is running')
bot.infinity_polling()


