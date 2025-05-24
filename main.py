from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message:types.Message):
    await message.reply("Привет! Я бот!")
@dp.message_handler(commands=["puk"])
async def echo(message: types.Message):
    await message.reply(f"Ты сказал: {message.text}")

if __name__ == "__main__":
    executor.start_polling(dp)
