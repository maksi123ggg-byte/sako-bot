import os
import asyncio
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "8586142798:AAEJ3iqff4TnmqM19e-enCzpLylaNe1-Ca0"
ADMIN_ID = 8341066688
GOLDEN_KEY = "v1frcp8yh3dqtkt14p5xwp82juxlw1rj"

FUNPAY_URL = "https://funpay.com"
PAYGAME_URL = "https://paygame.ru"
REVIEWS_URL = "https://funpay.com"
SUPPORT_URL = "https://t.me"

bot = Bot(token=TOKEN)
dp = Dispatcher()

AUTORAISE_ENABLED = True

products = {
    "7-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "230 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "7-Я|СОПРОВОД|ГАРАНТ 50КК+ШМОТ": "450 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 10КК+ШМОТ": "150 ₽",
    "5-Я|СОПРОВОД|ГАРАНТ 20КК+ШМОТ": "250 ₽",
    "7-Я|БУСТ|20КК-БЕЗ ШМОТА": "200 ₽",
    "7-Я|БУСТ|50КК-БЕЗ ШМОТА": "400 ₽"
}

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Бот активен и работает!".encode("utf-8"))

    def log_message(self, format, *args):
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(("", port), PingHandler)
    httpd.serve_forever()

def get_free_proxies():
    urls = [
        "https://githubusercontent.com",
        "https://proxyscrape.com"
    ]
    proxies = []
    for url in urls:
        try:
            response = requests.get(url, timeout=4)
            if response.status_code == 200:
                proxies.extend(response.text.strip().split("\n"))
        except:
            continue
    return [p.strip() for p in proxies if p.strip()]

def raise_funpay_lots():
    url = "https://funpay.com"
    headers = {
        "Cookie": f"golden_key={GOLDEN_KEY}",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://funpay.com",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Connection": "keep-alive"
    }
    data = {"game_id": ""} 
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=5)
        if response.status_code == 200:
            return True, "Лоты успешно обработаны напрямую без ограничений"
    except:
        pass

    proxy_list = get_free_proxies()
    checked = 0
    for proxy in proxy_list:
        if checked >= 25:
            break
        if not proxy or ":" not in proxy:
            continue
        
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        try:
            checked += 1
            response = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=4)
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if "error" in json_data:
                        return False, f"Запрос дошел, но сайт вернул кулдаун: {json_data.get('message')}"
                except:
                    pass
                return True, f"Лоты подняты через прокси [{proxy}]"
        except:
            continue
            
    return False, "Все прокси заблокированы Cloudflare. Требуется обновление пула адресов."

async def funpay_loop():
    global AUTORAISE_ENABLED
    await asyncio.sleep(15)
    
    while True:
        if AUTORAISE_ENABLED:
            loop = asyncio.get_event_loop()
            success, info = await loop.run_in_executor(None, raise_funpay_lots)
            try:
                if success:
                    await bot.send_message(chat_id=ADMIN_ID, text=f"[FunPay] Автоподнятие выполнено успешно! 🔄\nИнфо: {info}")
                    await asyncio.sleep(7200)
                else:
                    await bot.send_message(chat_id=ADMIN_ID, text=f"[FunPay] Временный сбой сети ❌\nИнфо: {info}\nСледующая попытка через 1 час.")
                    await asyncio.sleep(3600)
            except Exception as tg_err:
                print(f"Ошибка отправки сообщения: {tg_err}")
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)

@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    await message.answer(
        "🎒 Добро пожаловать в METRO ROYALE SHOP от клана SK¹!\n\n"
        "Мы — профессиональная команда клана SK¹. Предоставляем топовые услуги качественного сопровождения и буста в PUBG Mobile.\n\n"
        "🔒 Почему выбирают клан SK¹:\n"
        "• Профессиональные бойцы нашего клана\n"
        "• Быстрое выполнение и гарантия окупаемости\n"
        "• Полная безопасность вашего игрового аккаунта\n"
        "• Честные цены и сотни довольных клиентов\n\n"
        "Выбирайте нужный раздел в меню ниже 👇",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "view_products")
async def show_products(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for idx, (product, price) in enumerate(products.items()):
        kb.button(text=f"{product} — {price}", callback_data=f"prod:{idx}")
        
    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    
    await callback.message.edit_text(
        "📱 СПИСОК ДОСТУПНЫХ УСЛУГ КЛАНА SK¹\n\n"
        "Выберите интересующий вас вариант, чтобы открыть площадки для оплаты:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("prod:"))
async def select_platform(callback: CallbackQuery):
    data_parts = callback.data.split(":")
    if len(data_parts) < 2:
        await callback.answer("Ошибка данных товара", show_alert=True)
        return
        
    prod_idx = int(data_parts[1])
    product_name = list(products.keys())[prod_idx]
    product_price = list(products.values())[prod_idx]
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Купить на FunPay", url=FUNPAY_URL)
    kb.button(text="💳 Купить на PayGame", url=PAYGAME_URL)
    kb.button(text="⬅️ Назад к услугам SK¹", callback_data="view_products")
    kb.adjust(1)
    
    await callback.message.edit_text(
        f"🛒 Вы выбрали услугу от клана SK¹:\n• **{product_name}**\n\n"
        f"💰 Цена услуги: **{product_price}**\n\n"
        f"Выберите удобную для вас торговую площадку для безопасной покупки у нашего клана:",
        reply_markup=kb.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Услуги клана SK¹", callback_data="view_products")
    kb.button(text="⭐ Отзывы клиентов", url=REVIEWS_URL)
    kb.button(text="💬 Связаться с админом", url=SUPPORT_URL)
    kb.adjust(1)
    
    message_text = (
        "🎒 Добро пожаловать в METRO ROYALE SHOP от клана SK¹!\n\n"
        "Выбирайте нужный раздел в меню ниже 👇"
    )
    await callback.message.edit_text(message_text, reply_markup=kb.as_markup())
    await callback.answer()

def get_admin_kb():
    kb = InlineKeyboardBuilder()
    status = "🟢 ВКЛЮЧЕНО" if AUTORAISE_ENABLED else "🔴 ВЫКЛЮЧЕНО"
    
    kb.button(text="🟢 Включить автоподнятие", callback_data="fp_on")
    kb.button(text="🔴 Выключить автоподнятие", callback_data="fp_off")
    kb.button(text="⚡ Поднять прямо сейчас", callback_data="fp_now")
    kb.adjust(1)
    return kb.as_markup(), status

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    reply_markup, status = get_admin_kb()
    await message.answer(
        f"🤖 **АДМИН-ПАНЕЛЬ FUNPAY**\n"
        f"└ Текущий статус автоподнятия: {status}\n\n"
        f"Управляйте скриптом с помощью кнопок ниже:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "fp_on")
async def fp_on(callback: CallbackQuery):
    global AUTORAISE_ENABLED
    if callback.from_user.id != ADMIN_ID: return
    
    AUTORAISE_ENABLED = True
    reply_markup, status = get_admin_kb()
    await callback.message.edit_text(f"🤖 **АДМИН-ПАНЕЛЬ FUNPAY**\n└ Текущий статус автоподнятия: {status}\n\nРежим успешно изменен!", reply_markup=reply_markup, parse_mode="Markdown")
    await callback.answer("Автоподнятие включено! ✅")

@dp.callback_query(F.data == "fp_off")
async def fp_off(callback: CallbackQuery):
    global AUTORAISE_ENABLED
    if callback.from_user.id != ADMIN_ID: return
    
    AUTORAISE_ENABLED = False
    reply_markup, status = get_admin_kb()
    await callback.message.edit_text(f"🤖 **АДМИН-ПАНЕЛЬ FUNPAY**\n└ Текущий статус автоподнятия: {status}\n\nРежим успешно изменен!", reply_markup=reply_markup, parse_mode="Markdown")
    await callback.answer("Автоподнятие отключено! 🔴")

@dp.callback_query(F.data == "fp_now")
async def fp_now(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await callback.answer("Запрос отправлен...")
    
    loop = asyncio.get_event_loop()
    success, info = await loop.run_in_executor(None, raise_funpay_lots)
    if success:
        await callback.message.answer(f"[FunPay] Результат выполнения ⚡✅\n{info}")
    else:
        await callback.message.answer(f"[FunPay]
        Результат выполнения ❌\n{info}")

async def main():
    asyncio.create_task(funpay_loop())
    await dp.start_polling(bot)

if name == "main":
    threading.Thread(target=run_dummy_server,daemon=True).start()
    asyncio.run(main())
