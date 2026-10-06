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
    bot.send_message(
        msg.chat.id,
        "🛒 سبد خرید شما خالی است."
    )
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
        carts[user_id] = []
    carts[user_id].append(product_id)
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

print('bot is running')
bot.infinity_polling()


