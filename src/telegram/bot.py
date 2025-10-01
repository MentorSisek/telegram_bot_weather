from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand

from config import settings
from telegram.handlers import router
from telegram.middlewares import DependencyMiddleware

bot = Bot(token=settings.bot_token)

dp = Dispatcher(storage=RedisStorage.from_url(settings.redis_url_telegram))
dp.include_router(router)
dp.message.outer_middleware(DependencyMiddleware())


async def run():
	await bot.set_my_commands(
		commands=[
			BotCommand(command='start', description='Приветствие и запуск бота'),
			BotCommand(
				command='weather', description='Узнать погоду: /weather <город>'
			),
			BotCommand(command='celsius', description='Переключить единицы на °C'),
			BotCommand(command='fahrenheit', description='Переключить единицы на °F'),
		]
	)
	await dp.start_polling(bot)
