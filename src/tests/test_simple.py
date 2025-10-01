from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, Message, User

from telegram.handlers import start_handler, weather_handler


class TestWeatherBot:
	@pytest.fixture
	def mock_message(self):
		"""Создаем моковое сообщение."""
		message = MagicMock(spec=Message)
		message.from_user = MagicMock(spec=User)
		message.chat = MagicMock(spec=Chat)
		message.answer = AsyncMock()
		message.reply = AsyncMock()
		return message

	@pytest.mark.asyncio
	async def test_start_command(self, mock_message):
		"""Тест команды /start."""
		await start_handler(mock_message)

		# Проверяем, что бот ответил приветствием
		mock_message.answer.assert_called_once()
		reply_text = mock_message.answer.call_args[0][0]
		assert 'Привет! Я бот прогноза погоды' in reply_text
		assert '/weather' in reply_text

	@pytest.mark.asyncio
	async def test_weather_command_success(self, mock_message):
		"""Тест успешного запроса погоды."""
		mock_message.text = '/weather Moscow'

		# Создаем моковый клиент
		mock_client = MagicMock()
		mock_client.get_weather = AsyncMock(
			return_value={
				'current_weather': {
					'temperature': 15.5,
					'windspeed': 3.2,
					'time': '2025-01-01T12:00',
				}
			}
		)
		mock_client.format_weather.return_value = (
			'🌡 Температура: 15.5°C\n💨 Ветер: 3.2 м/с'
		)

		await weather_handler(mock_message, mock_client, 'celsius')

		# Проверяем, что клиент был вызван с правильными параметрами
		mock_client.get_weather.assert_called_once_with(city='Moscow', units='celsius')
		mock_message.reply.assert_called_once_with(
			'🌡 Температура: 15.5°C\n💨 Ветер: 3.2 м/с'
		)

	@pytest.mark.asyncio
	async def test_weather_command_no_city(self, mock_message):
		"""Тест команды /weather без города."""
		mock_message.text = '/weather'

		mock_client = MagicMock()

		await weather_handler(mock_message, mock_client, 'celsius')

		# Проверяем, что бот просит указать город
		mock_message.answer.assert_called_once_with('⚠ Укажи город: /weather Moscow')
		mock_client.get_weather.assert_not_called()
