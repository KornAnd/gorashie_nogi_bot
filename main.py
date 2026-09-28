import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils import format_hr_zones_text, pace_to_speed_text, speed_to_pace_text, SHOE_SIZE_CHART

BOT_TOKEN = "8890631054:AAHA3rEfyyBXMRfisCek2A-ZRjdCGoQYPxk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния FSM
class Form(StatesGroup):
    waiting_for_hr = State()
    waiting_for_pace = State()
    waiting_for_speed = State()
    waiting_for_shoe_size = State()

# Клавиатура главного меню
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💓 Пульсовые зоны"), KeyboardButton(text="⚡ Темп ↔ Скорость")],
            [KeyboardButton(text="📏 Дистанция / Время"), KeyboardButton(text="👟 Размер кроссовок")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🔥 Привет! Я беговой помощник чата **«Горящие Ноги»**!\n\n"
        "Выберите калькулятор в меню ниже 👇",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# 1. Пульсовые зоны
@dp.message(F.text == "💓 Пульсовые зоны")
async def hr_prompt(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_hr)
    await message.answer("Введите ваш **максимальный пульс ($ЧСС_{max}$)**, например `185`:", parse_mode="Markdown")

@dp.message(Form.waiting_for_hr)
async def hr_process(message: types.Message, state: FSMContext):
    try:
        hr_max = int(message.text)
        text = format_hr_zones_text(hr_max)
        await message.answer(text, parse_mode="Markdown")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введите число (например, 180):")

# 2. Темп ↔ Скорость
@dp.message(F.text == "⚡ Темп ↔ Скорость")
async def pace_speed_prompt(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Темп ➔ Скорость", callback_data="convert_pace")],
        [InlineKeyboardButton(text="Скорость ➔ Темп", callback_data="convert_speed")]
    ])
    await message.answer("Что перевести?", reply_markup=kb)

@dp.callback_query(F.data == "convert_pace")
async def ask_pace(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_pace)
    await call.message.answer("Введите темп в формате `МИН:СЕК` (например, `04:45`):", parse_mode="Markdown")
    await call.answer()

@dp.message(Form.waiting_for_pace)
async def process_pace(message: types.Message, state: FSMContext):
    res = pace_to_speed_text(message.text.strip())
    await message.answer(res, parse_mode="Markdown")
    await state.clear()

@dp.callback_query(F.data == "convert_speed")
async def ask_speed(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_speed)
    await call.message.answer("Введите скорость в км/ч (например, `12.5`):", parse_mode="Markdown")
    await call.answer()

@dp.message(Form.waiting_for_speed)
async def process_speed(message: types.Message, state: FSMContext):
    try:
        sp = float(message.text.replace(',', '.'))
        res = speed_to_pace_text(sp)
        await message.answer(res, parse_mode="Markdown")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Введите числовое значение скорости (например 12.5):")

# 3. Кроссовки
@dp.message(F.text == "👟 Размер кроссовок")
async def shoe_prompt(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_shoe_size)
    await message.answer("Введите ваш размер в **US** (например `10` или `9.5`):", parse_mode="Markdown")

@dp.message(Form.waiting_for_shoe_size)
async def shoe_process(message: types.Message, state: FSMContext):
    try:
        us_val = float(message.text.replace(',', '.'))
        # Находим подходящую строку в таблице
        match = None
        for row in SHOE_SIZE_CHART["man"]:
            if abs(row["us"] - us_val) < 0.3:
                match = row
                break
        
        if match:
            res = (
                f"👟 **Соответствие размеров (Мужские)**:\n\n"
                f"• **US**: {match['us']}\n"
                f"• **UK**: {match['uk']}\n"
                f"• **EUR**: {match['eur']}\n"
                f"• **RUS**: {match['rus']}\n"
                f"• **Длина стопы (CM)**: {match['cm']} см"
            )
            await message.answer(res, parse_mode="Markdown")
        else:
            await message.answer("Размер не найден в таблице. Попробуйте US от 7 до 13.")
        await state.clear()
    except ValueError:
        await message.answer("⚠️ Введите числовое значение (например 10):")

async def main():
    print("🤖 Чисто текстовый бот 'Горящие Ноги' запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
