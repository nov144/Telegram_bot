import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

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

# Подключение к Google Таблице
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
SPREADSHEET_ID = "130eO8Wl9ezkXEgbM6CnHt6C2k_lFKYKttbDqfN69mxg"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

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
    await BookingStates.waiting_for_date.set()

# Обработка даты
@router.callback_query()
async def process_date(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state != BookingStates.waiting_for_date.state:
        await callback.answer()
        return

    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback)

    if not selected:
        await callback.answer()
        return

    await state.update_data(date=str(date))
    await callback.message.answer(f"Вы выбрали: {date.strftime('%d.%m.%Y')}")
    await callback.message.answer("Введите номер телефона:")
    await state.set_state(BookingStates.waiting_for_phone)
    await callback.answer()


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

    # Сохраняем в Google Таблицу
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    sheet.append_row([name, date, phone, timestamp])

    await message.answer(summary)

    # Отправка мастеру
    await bot.send_message(-1002293928496, summary)  # Группа
    await bot.send_message(300466559, summary)       # Личный ID

    await state.finish()

# Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

