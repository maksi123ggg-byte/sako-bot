import os
import asyncio
from threading import Thread
import http.server
import socketserver
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8586142798:AAEJ3iqff4TnmqM19e-encZphrJb9G_fC0M"

FUNPAY_URL = "https://funpay.com"
PAYGAME_URL = "https://paygame.ru"
SUPPORT_URL = "https://t.me"

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    await message.answer(
        "🎒 **Добро пожаловать в METRO ROYALE SHOP от клана SK¹!**\n\n"
        "Мы — профессиональная команда клана **SK¹**. Предоставляем топовые услуги буста в PUBG Mobile.\n\n"
        "🔒 **Наши гарантии:**\n"
        "• Быстрое выполнение\n"
        "• Полная безопасность аккаунта\n"
        "• Честные цены\n\n"
        "Выбирайте нужный раздел в меню नीचे 👇",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "view_products")
async def show_products(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for product, price in products.items():
        kb.button(text=f"{product} — {price}", callback_data=f"buy_{price}")
        
    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    
    await callback.message.edit_text(
        "📱 **СПИСОК ДОСТУПНЫХ УСЛУГ КЛАНА SK¹**\n\n"
        "Выберите интересующий вас вариант:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def select_platform(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить на FunPay", url=FUNPAY_URL)
    kb.button(text="💳 Купить на PayGame", url=PAYGAME_URL)
    kb.button(text="⬅️ Назад к услугам SK¹", callback_data="view_products")
    kb.adjust(1)
    
    await callback.message.edit_text(
        "🛒 **Вы выбрали услугу от клана SK¹!**\n\n"
        "Выберите удобную торговую площадку для безопасной покупки:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    await callback.message.edit_text(
        "🎒 **Добро пожаловать в METRO ROYALE SHOP от клана SK¹!**\n\n"
        "Выбирайте нужный раздел ниже 👇",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    Thread(target=run_dummy_server, daemon=True).start()
    asyncio.run(main())
    
