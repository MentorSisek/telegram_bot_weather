from typing import Literal

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Location, Message

from openmeteo.client import OpenMeteoClient

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
	await message.answer(
		'👋 Привет! Я бот прогноза погоды.\n'
		'Используй команду:\n'
		'• /weather <город> — узнать погоду в городе\n'
		'• Отправь геолокацию — погода по координатам\n'
		'• /celsius или /fahrenheit — переключение единиц измерения'
	)


@router.message(Command('weather'))
async def weather_handler(
	message: Message,
	openmeteo_client: OpenMeteoClient,
	metric: Literal['fahrenheit', 'celsius'],
):
	args = message.text.split(maxsplit=1)  # type: ignore
	if len(args) < 2:
		await message.answer('⚠ Укажи город: /weather Moscow')
		return

	city = args[1]
	data = await openmeteo_client.get_weather(city=city, units=metric)
	if not data:
		await message.reply('😔 Не удалось найти город. Попробуй другой.')
		return

	await message.reply(openmeteo_client.format_weather(data, metric))


@router.message(F.location)
async def location_handler(
	message: Message,
	openmeteo_client: OpenMeteoClient,
	metric: Literal['fahrenheit', 'celsius'],
):
	loc: Location = message.location  # type: ignore
	data = await openmeteo_client.get_weather(
		lat=loc.latitude, lon=loc.longitude, units=metric
	)
	if not data:
		await message.reply('😔 Не удалось найти город. Попробуй другой.')
		return

	await message.reply(openmeteo_client.format_weather(data, metric))


@router.message(Command('celsius'))
async def set_celsius(message: Message, state: FSMContext):
	await state.update_data(metric='celsius')
	await message.reply('✅ Единицы измерения: градусы Цельсия (°C)')


@router.message(Command('fahrenheit'))
async def set_fahrenheit(message: Message, state: FSMContext):
	await state.update_data(metric='fahrenheit')
	await message.reply('✅ Единицы измерения: градусы Фаренгейта (°F)')
