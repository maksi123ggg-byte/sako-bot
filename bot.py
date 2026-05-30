from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "8586142798:AAEJ3iqff4TnmqM19e-enCzpLylaNe1-Ca0"

FUNPAY_URL = "https://funpay.com/uk/users/19612186/"
PAYGAME_URL = "https://paygame.ru/users/SAKO1"
REVIEWS_URL = "https://funpay.com/uk/users/19612186/"
SUPPORT_URL = "https://t.me/SK_SAKO"

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
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    await message.answer(
        "🎒 Добро пожаловать в METRO ROYALE SHOP от клана SK¹!\n\n"
        "Выбирайте нужный раздел в меню ниже 👇",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "view_products")
async def show_products(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for idx, (product, price) in enumerate(products.items()):
        kb.button(text=f"{product} — {price}", callback_data=f"prod:{idx}")
        
    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    
    await callback.message.edit_text(
        "📱 СПИСОК УСЛУГ\n\nВыберите услугу:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("prod:"))
async def select_product(callback: CallbackQuery):
    prod_idx = int(callback.data.split(":")[1])
    product_name = list(products.keys())[prod_idx]
    product_price = list(products.values())[prod_idx]
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить на FunPay", url=FUNPAY_URL)
    kb.button(text="💳 Купить на PayGame", url=PAYGAME_URL)
    kb.button(text="⬅️ Назад", callback_data="view_products")
    kb.adjust(1)
    
    await callback.message.edit_text(
        f"🛒 {product_name}\n\n💰 Цена: {product_price}",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    await callback.message.edit_text(
        "🎒 Главное меню\n\nВыбирайте 👇",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
