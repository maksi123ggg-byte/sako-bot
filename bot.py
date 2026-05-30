import os
import asyncio
from threading import Thread
import http.server
import socketserver
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен вашего бота
TOKEN = "8586142798:AAEJ3iqff4TnmqM19e-encZphrJb9G_fC0M"

# Ваши реальные контакты и ссылки
FUNPAY_URL = "https://funpay.com"
PAYGAME_URL = "https://paygame.ru"
REVIEWS_URL = "https://funpay.com"
SUPPORT_URL = "https://t.me"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список товаров клана SK¹
products = {
    "7-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "230 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 50КК+ШМОТ": "450 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "250 ₽",
    "7-Я|БУСТ|20КК-БЕЗ ШМОТА": "200 ₽",
    "7-Я|БУСТ|50КК-БЕЗ ШМОТА": "400 ₽"
}

# 1. Главное меню бота (Клан SK¹)
@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    await message.answer(
        "🎒 **Добро пожаловать в METRO ROYALE SHOP от клана SK¹!**\n\n"
        "Мы — профессиональная команда клана **SK¹**. Предоставляем топовые услуги качественного сопровождения и буста в PUBG Mobile.\n\n"
        "🔒 **Почему выбирают клан SK¹:**\n"
        "• Профессиональные бойцы нашего клана\n"
        "• Быстрое выполнение и гарантия окупаемости\n"
        "• Полная безопасность вашего игрового аккаунта\n"
        "• Честные цены и сотни довольных клиентов\n\n"
        "Выбирайте нужный раздел в меню ниже 👇",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )

# 2. Окно со списком услуг клана SK¹
@dp.callback_query(F.data == "view_products")
async def show_products(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for idx, (product, price) in enumerate(products.items()):
        kb.button(text=f"{product} — {price}", callback_data=f"prod:{idx}")
        
    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    
    await callback.message.edit_text(
        "📱 **СПИСОК ДОСТУПНЫХ УСЛУГ КЛАНА SK¹**\n\n"
        "Выберите интересующий вас вариант, чтобы открыть площадки для оплаты:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

# 3. Карточка товара с упоминанием SK¹
@dp.callback_query(F.data.startswith("prod:"))
async def select_platform(callback: CallbackQuery):
    prod_idx = int(callback.data.split(":")[1])
    product_name = list(products.keys())[prod_idx]
    product_price = list(products.values())[prod_idx]
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить на FunPay", url=FUNPAY_URL)
    kb.button(text="💳 Купить на PayGame", url=PAYGAME_URL)
    kb.button(text="⬅️ Назад к услугам SK¹", callback_data="view_products")
    kb.adjust(1)
    
    await callback.message.edit_text(
        f"🛒 **Вы выбрали услугу от клана SK¹:**\n`{product_name}`\n\n"
        f"💰 **Цена услуги:** {product_price}\n\n"
        f"Выберите удобную для вас торговую площадку для безопасной покупки у нашего клана:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

# 4. Возврат в главное меню
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    message_text = (
        "🎒 **Добро пожаловать в METRO ROYALE SHOP от клана SK¹!**\n\n"
        "Выбирайте нужный раздел в меню ниже 👇"
    )
    await callback.message.edit_text(message_text, reply_markup=kb.as_markup())
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
    
