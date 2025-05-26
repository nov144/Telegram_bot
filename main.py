from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from aiogram_calendar import simple_cal_callback, SimpleCalendar
from states import BookingStates
import os

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Команда /start
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Записаться"))
    await message.answer("Привет! Я бот для записи к мастеру. Выберите действие:", reply_markup=keyboard)

# Нажатие "Записаться"
@dp.message_handler(lambda message: message.text == "Записаться")
async def start_booking(message: types.Message):
    await message.answer("Как вас зовут?")
    await BookingStates.waiting_for_name.set()

# Получаем имя
@dp.message_handler(state=BookingStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer("Выберите дату записи:", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        "Пожалуйста, выберите дату:",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await BookingStates.waiting_for_date.set()  # ← ВАЖНО

# Обработка даты
@dp.callback_query_handler(simple_cal_callback.filter(), state=BookingStates.waiting_for_date)
async def process_date(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if not selected:
        return

    await state.update_data(date=str(date))
    await callback_query.message.answer(f"Вы выбрали: {date.strftime('%d.%m.%Y')}")
    await callback_query.answer()

    await callback_query.message.answer("Введите номер телефона:")
    await BookingStates.waiting_for_phone.set()

# Получаем телефон
@dp.message_handler(state=BookingStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)

    data = await state.get_data()
    name = data["name"]
    date = data["date"]

    summary = (
        f"Запись подтверждена!\n\n"
        f"Имя: {name}\n"
        f"Дата: {date}\n"
        f"Телефон: {phone}"
    )

    await message.answer(summary)

    # Отправка владельцу (замени chat_id при необходимости)
    await bot.send_message(-1002293928496, summary)  # группа
    await bot.send_message(300466559, summary)       # личка

    await state.finish()

# Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)




