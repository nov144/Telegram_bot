from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from states import BookingStates
import os

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"))  # BOT_TOKEN из Render переменной
storage = MemoryStorage()  # FSM-хранилище
dp = Dispatcher(bot, storage=storage)

# Обработка /start
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Записаться"))
    keyboard.add(KeyboardButton("Контакты"))
    await message.answer("Привет! Я бот для записи к мастеру. Выберите действие:", reply_markup=keyboard)

# Нажатие на кнопку "Записаться"
@dp.message_handler(lambda message: message.text == "Записаться")
async def start_booking(message: types.Message):
    await message.answer("Как вас зовут?")
    await BookingStates.waiting_for_name.set()  # переключаемся в состояние "ждём имя"

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
