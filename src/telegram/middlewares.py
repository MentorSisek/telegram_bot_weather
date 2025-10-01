from collections.abc import Awaitable, Callable
from typing import Any, Literal

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from config import settings
from openmeteo.client import OpenMeteoClient


async def get_metric(state: FSMContext) -> Literal['fahrenheit', 'celsius']:
	data = await state.get_data()
	metric = data.get('metric')
	if metric:
		return metric
	return 'celsius'


class DependencyMiddleware(BaseMiddleware):
	def __init__(self) -> None:
		super().__init__()
		self.openmeteo_client = OpenMeteoClient(settings.redis_url_openmeteo)

	async def __call__(
		self,
		handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
		event: TelegramObject,
		data: dict[str, Any],
	) -> Any:
		state: FSMContext = data['state']
		data['metric'] = await get_metric(state)
		data['openmeteo_client'] = self.openmeteo_client
		result = await handler(event, data)
		return result
