import os
import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession

BOT_TOKEN = "8890631054:AAHA3rEfyyBXMRfisCek2A-ZRjdCGoQYPxk"

# Подключение через прокси PythonAnywhere
session = AiohttpSession(proxy="http://proxy.server:3128")
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

# --- FSM Состояния ---
class Form(StatesGroup):
    waiting_hr_max = State()
    waiting_hr_age = State()
    
    pace_to_speed = State()
    speed_to_pace = State()
    
    dist_time_for_pace = State()
    shoe_size = State()

# --- Главное меню ---
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💓 Пульсовые зоны"), KeyboardButton(text="⚡ Темп ↔ Скорость")],
            [KeyboardButton(text="📏 Дистанция / Время ➔ Темп"), KeyboardButton(text="👟 Размер кроссовок")]
        ],
        resize_keyboard=True
    )

# --- Универсальный парсер времени ---
def parse_time_to_seconds(time_str: str) -> int:
    """
    Разбирает время из самых разных форматов:
    '03:30:00' -> 3 часа 30 минут
    '3:30:00'  -> 3 часа 30 минут
    '03:30'    -> 3 часа 30 минут (если первое число <= 5 и контекст марафона/длинной дистанции) ИЛИ 3 мин 30 сек
    '50:00'    -> 50 минут
    '1:45:00'  -> 1 час 45 минут
    Разделителями могут быть двоеточие, точка или запятая.
    """
    cleaned = re.sub(r'[.,;]', ':', time_str.strip())
    parts = [int(p) for p in cleaned.split(':') if p.isdigit()]
    
    if len(parts) == 3:
        # ЧЧ:ММ:СС
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        val1, val2 = parts[0], parts[1]
        # Если формат вида 3:30 или 03:30 для марафона - это 3 часа 30 минут (12600 сек)
        # Если человек бежит марафон/длинную дистанцию, 3:30 - это 3 часа 30 мин!
        # Но если 50:00 - это 50 минут.
        # Анализируем: если val1 <= 5, вероятнее всего человек имеет в виду ЧАШИ:МИНУТЫ (например 3:30 или 4:15)
        # Если val1 > 5 (например 25:30 или 50:00), это МИНУТЫ:СЕКУНДЫ
        if val1 <= 5:
            return val1 * 3600 + val2 * 60
        else:
            return val1 * 60 + val2
    elif len(parts) == 1:
        # Только минуты
        return parts[0] * 60
    else:
        raise ValueError("Неверный формат времени")

# --- Форматирование Пульсовых Зон ---
def calc_hr_zones(hr_max: int) -> str:
    z1_min, z1_max = round(hr_max * 0.60), round(hr_max * 0.70)
    z2_min, z2_max = round(hr_max * 0.70), round(hr_max * 0.75)
    z3_min, z3_max = round(hr_max * 0.75), round(hr_max * 0.85)
    z4_min, z4_max = round(hr_max * 0.85), round(hr_max * 0.95)
    z5_min, z5_max = round(hr_max * 0.95), hr_max

    return (
        f"📊 <b>РАСЧЁТ ПУЛЬСОВЫХ ЗОН</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Максимальный пульс (ЧСС max): <b>{hr_max} уд/мин</b>\n\n"
        f"🟦 <b>Зона 1 (Медленный бег / Восстановление)</b>\n"
        f"└ Диапазон: <code>{z1_min} - {z1_max} уд/мин</code> (60-70%)\n"
        f"└ Целевой: <b>{round(hr_max*0.69)} уд/мин</b>\n\n"
        f"🟩 <b>Зона 2 (Легкий / Аэробный темп)</b>\n"
        f"└ Диапазон: <code>{z2_min} - {z2_max} уд/мин</code> (70-75%)\n"
        f"└ Целевой: <b>{round(hr_max*0.74)} уд/мин</b>\n\n"
        f"🟨 <b>Зона 3 (Темповой бег)</b>\n"
        f"└ Диапазон: <code>{z3_min} - {z3_max} уд/мин</code> (75-85%)\n"
        f"└ Целевой: <b>{round(hr_max*0.83)} уд/мин</b>\n\n"
        f"🟧 <b>Зона 4 (Бег на уровне ПАНО)</b>\n"
        f"└ Диапазон: <code>{z4_min} - {z4_max} уд/мин</code> (85-95%)\n"
        f"└ Целевой: <b>{round(hr_max*0.92)} уд/мин</b>\n\n"
        f"🟥 <b>Зона 5 (Максимальная нагрузка / МПК)</b>\n"
        f"└ Диапазон: <code>{z5_min} - {z5_max} уд/мин</code> (95-100%)\n"
        f"└ Целевой: <b>{round(hr_max*0.97)} уд/мин</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

# --- Справочная таблица кроссовок ---
SHOE_TABLE = [
    {"us": 7.0, "uk": 6.5, "eur": 40.0, "rus": 39.0, "cm": 25.0},
    {"us": 7.5, "uk": 7.0, "eur": 40.5, "rus": 39.5, "cm": 25.5},
    {"us": 8.0, "uk": 7.5, "eur": 41.0, "rus": 40.0, "cm": 26.0},
    {"us": 8.5, "uk": 8.0, "eur": 42.0, "rus": 41.0, "cm": 26.5},
    {"us": 9.0, "uk": 8.5, "eur": 42.5, "rus": 41.5, "cm": 27.0},
    {"us": 9.5, "uk": 9.0, "eur": 43.0, "rus": 42.0, "cm": 27.5},
    {"us": 10.0, "uk": 9.5, "eur": 44.0, "rus": 42.5, "cm": 28.0},
    {"us": 10.5, "uk": 10.0, "eur": 44.5, "rus": 43.0, "cm": 28.5},
    {"us": 11.0, "uk": 10.5, "eur": 45.0, "rus": 43.5, "cm": 29.0},
    {"us": 11.5, "uk": 11.0, "eur": 45.5, "rus": 44.0, "cm": 29.5},
    {"us": 12.0, "uk": 11.5, "eur": 46.0, "rus": 44.5, "cm": 30.0},
]

# --- Старт ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏃‍♂️ <b>БЕГОВОЙ ПОМОЩНИК «ГОРЯЩИЕ НОГИ»</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Привет! Я твой интерактивный беговой калькулятор.\n\n"
        "💡 <i>Подсказка: Для начала работы выберите нужный инструмент в меню ниже 👇</i>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

# ---------------- 1. ПУЛЬСОВЫЕ ЗОНЫ ----------------
@dp.message(F.text == "💓 Пульсовые зоны")
async def hr_menu(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Ввести точный ЧСС max", callback_data="hr_by_max")],
        [InlineKeyboardButton(text="🎂 Рассчитать по возрасту (220 - возраст)", callback_data="hr_by_age")]
    ])
    await message.answer(
        "💓 <b>КАЛЬКУЛЯТОР ПУЛЬСОВЫХ ЗОН</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Рассчитывает 5 тренировочных пульсовых зон. Выберите точный ввод ЧСС max (если сдавали тредмил-тест) или автоматический расчёт по возрасту.</i>\n\n"
        "👇 <b>Выберите способ расчёта:</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "hr_by_max")
async def hr_by_max_handler(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_hr_max)
    await call.message.answer(
        "✏️ <b>Введите ваш максимальный пульс (ЧСС max):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Отправьте число от 100 до 230 уд/мин.</i>\n\n"
        "📌 <i>Пример: <code>185</code></i>",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(Form.waiting_hr_max)
async def process_hr_max(message: types.Message, state: FSMContext):
    try:
        clean_text = re.sub(r'[^\d]', '', message.text)
        hr = int(clean_text)
        if hr < 100 or hr > 240:
            await message.answer("⚠️ Пожалуйста, введите реальный пульс (от 100 до 240 уд/мин):")
            return
        res = calc_hr_zones(hr)
        await message.answer(res, parse_mode="HTML")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Введите только число (например, <code>185</code>):", parse_mode="HTML")

@dp.callback_query(F.data == "hr_by_age")
async def hr_by_age_handler(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_hr_age)
    await call.message.answer(
        "🎂 <b>Введите ваш возраст (полных лет):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Бот автоматически высчитает ЧСС max по формуле (220 - возраст).</i>\n\n"
        "📌 <i>Пример: <code>30</code></i>",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(Form.waiting_hr_age)
async def process_hr_age(message: types.Message, state: FSMContext):
    try:
        clean_text = re.sub(r'[^\d]', '', message.text)
        age = int(clean_text)
        if age < 10 or age > 100:
            await message.answer("⚠️ Пожалуйста, введите корректный возраст (от 10 до 100 лет):")
            return
        hr = 220 - age
        res = f"ℹ️ <i>Приблизительный ЧСС max для возраста {age} лет = {hr} уд/мин</i>\n\n" + calc_hr_zones(hr)
        await message.answer(res, parse_mode="HTML")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Введите число (например, <code>30</code>):", parse_mode="HTML")

# ---------------- 2. ТЕМП <-> СКОРОСТЬ ----------------
@dp.message(F.text == "⚡ Темп ↔ Скорость")
async def pace_speed_menu(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱️ Темп (мин/км) ➔ Скорость (км/ч)", callback_data="p2s")],
        [InlineKeyboardButton(text="🚀 Скорость (км/ч) ➔ Темп (мин/км)", callback_data="s2p")]
    ])
    await message.answer(
        "⚡ <b>КОНВЕРТЕР ТЕМПА И СКОРОСТИ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Переводит темп бега на улице в км/ч для беговой дорожки и наоборот.</i>\n\n"
        "👇 <b>Выберите направление конвертации:</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "p2s")
async def p2s_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.pace_to_speed)
    await call.message.answer(
        "✏️ <b>Введите темп (мин/км):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Принимаются форматы 05:30, 5:30, 5.30 или 5,30</i>\n\n"
        "📌 <i>Пример: <code>05:30</code> или <code>4:45</code></i>",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(Form.pace_to_speed)
async def process_p2s(message: types.Message, state: FSMContext):
    try:
        cleaned = re.sub(r'[.,;]', ':', message.text.strip())
        parts = [int(p) for p in cleaned.split(":") if p.isdigit()]
        if len(parts) < 2:
            raise ValueError()
        mins, secs = parts[0], parts[1]
        total_hours = (mins * 60 + secs) / 3600
        speed = round(1 / total_hours, 2)
        
        res = (
            f"📈 <b>РЕЗУЛЬТАТ КОНВЕРТАЦИИ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ Беговой темп: <b>{mins:02d}:{secs:02d} мин/км</b>\n"
            f"⚡ Скорость на дорожке: <b>{speed} км/ч</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(res, parse_mode="HTML")
        await state.clear()
    except Exception:
        await message.answer("⚠️ Неверный формат! Введите темп, например <code>05:30</code> или <code>5.30</code>", parse_mode="HTML")

@dp.callback_query(F.data == "s2p")
async def s2p_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.speed_to_pace)
    await call.message.answer(
        "✏️ <b>Введите скорость (км/ч):</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Вводите с точкой или запятой (12.5 или 12,5).</i>\n\n"
        "📌 <i>Пример: <code>12.5</code> или <code>10</code></i>",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(Form.speed_to_pace)
async def process_s2p(message: types.Message, state: FSMContext):
    try:
        clean_text = message.text.replace(",", ".").strip()
        sp = float(clean_text)
        total_secs = round(3600 / sp)
        mins = total_secs // 60
        secs = total_secs % 60
        
        res = (
            f"📈 <b>РЕЗУЛЬТАТ КОНВЕРТАЦИИ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Скорость на дорожке: <b>{sp} км/ч</b>\n"
            f"⏱️ Беговой темп: <b>{mins:02d}:{secs:02d} мин/км</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(res, parse_mode="HTML")
        await state.clear()
    except Exception:
        await message.answer("⚠️ Введите числовое значение (например, <code>12.5</code> или <code>12,5</code>):", parse_mode="HTML")

# ---------------- 3. ДИСТАНЦИЯ / ВРЕМЯ -> ТЕМП ----------------
@dp.message(F.text == "📏 Дистанция / Время ➔ Темп")
async def dist_time_menu(message: types.Message, state: FSMContext):
    await state.set_state(Form.dist_time_for_pace)
    await message.answer(
        "📏 <b>КАЛЬКУЛЯТОР ТЕМПА И СКОРОСТИ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Введите дистанцию (в километрах) и итоговое время пробежки через пробел. Разделителями времени могут быть двоеточие, точка или запятая.</i>\n\n"
        "✏️ <b>Формат ввода:</b> <code>ДИСТАНЦИЯ ВРЕМЯ</code>\n"
        "• Дистанция: <code>42</code>, <code>42.2</code> или <code>42,2</code>\n"
        "• Время на марафон: <code>3:30:00</code> или <code>03:30:00</code> (3 часа 30 минут)\n"
        "• Время на 10 км: <code>50:00</code> (50 минут)\n\n"
        "📌 <b>Примеры ввода:</b>\n"
        "• <code>42.2 03:30:00</code> (Марафон 42.2 км за 3ч 30м)\n"
        "• <code>10 50:00</code> (10 км за 50 минут)\n"
        "• <code>21.1 1:45:00</code> (Полумарафон за 1ч 45м)\n"
        "• <code>5 24.30</code> (5 км за 24м 30с)",
        parse_mode="HTML"
    )

@dp.message(Form.dist_time_for_pace)
async def process_dist_time(message: types.Message, state: FSMContext):
    try:
        text = message.text.strip()
        parts = text.split()
        if len(parts) != 2:
            raise ValueError()
        
        dist_str = parts[0].replace(",", ".")
        dist = float(dist_str)
        time_str = parts[1]
        
        total_sec = parse_time_to_seconds(time_str)
        
        pace_sec = round(total_sec / dist)
        p_min = pace_sec // 60
        p_sec = pace_sec % 60
        
        speed = round((dist / (total_sec / 3600)), 2)

        # Вывод красивого формата времени в ответе
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        if h > 0:
            pretty_time = f"{h} ч {m:02d} мин {s:02d} сек"
        else:
            pretty_time = f"{m} мин {s:02d} сек"

        res = (
            f"📊 <b>РЕЗУЛЬТАТ РАСЧЁТА</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 Дистанция: <b>{dist} км</b>\n"
            f"⏱️ Итоговое время: <b>{pretty_time}</b>\n\n"
            f"🔥 <b>Средний темп: {p_min:02d}:{p_sec:02d} мин/км</b>\n"
            f"⚡ Средняя скорость: <b>{speed} км/ч</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        await message.answer(res, parse_mode="HTML")
        await state.clear()
    except Exception:
        await message.answer(
            "⚠️ <b>Ошибка формата ввода!</b>\n"
            "Пожалуйста, введите дистанцию и время через пробел.\n"
            "Пример для марафона: <code>42.2 03:30:00</code> (42.2 км за 3 часа 30 минут)\n"
            "Пример для 10 км: <code>10 50:00</code>",
            parse_mode="HTML"
        )

# ---------------- 4. РАЗМЕР КРОССОВОК ----------------
@dp.message(F.text == "👟 Размер кроссовок")
async def shoe_menu(message: types.Message, state: FSMContext):
    await state.set_state(Form.shoe_size)
    
    table_preview = (
        "📋 <b>ШПАРГАЛКА ПОПУЛЯРНЫХ РАЗМЕРОВ:</b>\n"
        "<code>"
        "US  | EUR  | RUS  | CM (стопа)\n"
        "------------------------------\n"
        "8.0 | 41.0 | 40.0 | 26.0 см\n"
        "9.0 | 42.5 | 41.5 | 27.0 см\n"
        "10.0| 44.0 | 42.5 | 28.0 см\n"
        "11.0| 45.0 | 43.5 | 29.0 см\n"
        "</code>"
    )
    
    await message.answer(
        "👟 <b>КАЛЬКУЛЯТОР РАЗМЕРОВ КРОССОВОК</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Подсказка: Принимает размер US или CM в любых форматах (10, 10.5, 10,5, 28 см).</i>\n\n"
        f"{table_preview}\n\n"
        "✏️ <b>Введите точный размер US или стопу в СМ:</b>\n"
        "📌 <i>Пример: <code>10</code> (для US) или <code>28</code> (для СМ)</i>",
        parse_mode="HTML"
    )

@dp.message(Form.shoe_size)
async def process_shoe(message: types.Message, state: FSMContext):
    try:
        clean_text = re.sub(r'[^\d.,]', '', message.text).replace(",", ".")
        val = float(clean_text)
        match = None
        for r in SHOE_TABLE:
            if abs(r["us"] - val) < 0.3 or abs(r["cm"] - val) < 0.3:
                match = r
                break
        
        if match:
            res = (
                f"👟 <b>ТАБЛИЦА РАЗМЕРОВ ОБУВИ</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🇺🇸 <b>US (США)</b>: <code>{match['us']}</code>\n"
                f"🇬🇧 <b>UK (Великобритания)</b>: <code>{match['uk']}</code>\n"
                f"🇪🇺 <b>EUR (Европа)</b>: <code>{match['eur']}</code>\n"
                f"🇷🇺 <b>RUS (Россия)</b>: <code>{match['rus']}</code>\n"
                f"📏 <b>Длина стопы</b>: <code>{match['cm']} см</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            await message.answer(res, parse_mode="HTML")
        else:
            await message.answer("⚠️ Размер не найден в сетке. Попробуйте US от 7 до 12 или CM от 25 до 30.")
        await state.clear()
    except Exception:
        await message.answer("⚠️ Введите числовое значение (например, <code>10</code> или <code>28</code>):", parse_mode="HTML")

async def main():
    print("🤖 Стилизованный бот 'Горящие Ноги' с интеллектуальным парсингом времени запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
