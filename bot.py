import os
import asyncio
from threading import Thread
import http.server
import socketserver
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен из вашего скриншота и ваш Telegram ID
TOKEN = "8586142798:AAEJ3iqff4TnmqM19e-enCzpLylaNe1-Ca0"
ADMIN_ID = 8341066688

# Ваша ссылка на профиль FunPay оформлена верно
FUNPAY_URL = "https://funpay.com/uk/users/19612186/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Все ваши товары из скриншота
products = {
    "7-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "230 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 50КК+ШМОТ": "450 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "250 ₽",
    "7-Я|БУСТ|20КК-БЕЗ ШМОТА": "200 ₽",
    "7-Я|БУСТ|50КК-БЕЗ ШМОТА": "400 ₽"
}

@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    for product, price in products.items():
        # При нажатии пользователя перенаправит на ваш FunPay
        kb.button(
            text=f"{product} - {price}",
            url=FUNPAY_URL
        )
    kb.adjust(1)
    await message.answer(
        "📱 METRO ROYALE SHOP\n\nВыберите нужную услугу для покупки на FunPay:",
        reply_markup=kb.as_markup()
    )

async def main():
    await dp.start_polling(bot)

# Код для обхода ограничений Render
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    Thread(target=run_dummy_server, daemon=True).start()
    asyncio.run(main())
    
