import os
import asyncio
from threading import Thread
import http.server
import socketserver
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен и ID администратора
TOKEN = "8860147716:AAHksZ10JPU4B5TXCjqOaDx_-65341x8wqs"
ADMIN_ID = 8341066688

bot = Bot(token=TOKEN)
dp = Dispatcher()

products = {
    "60 UC": "99 ₽",
    "325 UC": "449 ₽",
    "660 UC": "849 ₽",
    "1800 UC": "2199 ₽",
    "3850 UC": "4399 ₽",
    "8100 UC": "8699 ₽"
}

user_orders = {}

@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    for product, price in products.items():
        kb.button(
            text=f"{product} - {price}",
            callback_data=f"buy:{product}"
        )
    kb.adjust(1)
    await message.answer(
        "📱 PUBG UC SHOP\n\nВыберите пакет UC:",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("buy:"))
async def select_product(callback: CallbackQuery):
    product = callback.data.split(":")[1]
    user_orders[callback.from_user.id] = product
    await callback.message.answer(
        f"Вы выбрали {product}\n\nОтправьте ваш PUBG ID."
    )
    await callback.answer()

@dp.message()
async def get_pubg_id(message: Message):
    user_id = message.from_user.id
    if user_id not in user_orders:
        await message.answer("Нажмите /start и выберите товар.")
        return
    product = user_orders[user_id]
    pubg_id = message.text
    username = message.from_user.username
    if username:
        username = f"@{username}"
    else:
        username = "нет username"
    await bot.send_message(
        ADMIN_ID,
        f"🛒 НОВЫЙ ЗАКАЗ\n\n"
        f"Товар: {product}\n"
        f"PUBG ID: {pubg_id}\n"
        f"Покупатель: {username}\n"
        f"Telegram ID: {user_id}"
    )
    await message.answer(
        "✅ Заказ принят.\nОжидайте сообщения от администратора."
    )
    del user_orders[user_id]

async def main():
    await dp.start_polling(bot)

# Специальная функция для Render, имитирующая работу веб-сайта
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    # Запускаем поддельный веб-порт в фоновом потоке, чтобы Render не ругался
    Thread(target=run_dummy_server, daemon=True).start()
    
    # Запускаем самого телеграм-бота
    asyncio.run(main())
    
