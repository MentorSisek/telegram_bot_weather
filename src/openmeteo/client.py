import json
import logging

import aiohttp

from .cache import Cache

logger = logging.getLogger('openmeteo')


class OpenMeteoClient:
	base_url: str = 'https://api.open-meteo.com/v1/forecast'
	geocode_url: str = 'https://nominatim.openstreetmap.org/search'
	unit_map: dict = {'celsius': 'metric', 'fahrenheit': 'imperial'}

	def __init__(self, redis_url_for_cache: str | None = None):
		self.cache = Cache(redis_url_for_cache)

	async def geocode_city(self, city: str):
		"""Преобразует название города в координаты через Nominatim"""
		key = f'geocode:{city}'

		cached = await self.cache.get(key)
		if cached:
			lat, lon = map(float, cached.split(','))
			return lat, lon

		params = {'q': city, 'format': 'json', 'limit': 1}
		async with aiohttp.ClientSession() as session:
			async with session.get(
				self.geocode_url, params=params, headers={'User-Agent': 'weather-bot'}
			) as resp:
				if resp.status != 200:
					return None
				data = await resp.json()
				if not data:
					return None
				lat, lon = float(data[0]['lat']), float(data[0]['lon'])

		await self.cache.set(key, f'{lat},{lon}')
		return lat, lon

	async def get_weather(
		self,
		units: str,
		city: str | None = None,
		lat: float | None = None,
		lon: float | None = None,
	):
		"""Запрос текущей погоды из Open-Meteo (по городу или координатам)"""
		units = self.unit_map[units]
		if city:
			coords = await self.geocode_city(city)
			if not coords:
				return None
			lat, lon = coords
			key = f'weather:city:{city}:{self.unit_map.get(units)}'
		elif lat and lon:
			key = f'weather:coords:{lat}:{lon}:{units}'
		else:
			return None

		cached = await self.cache.get(key)
		if cached:
			return json.loads(cached)

		params = {
			'latitude': lat,
			'longitude': lon,
			'current_weather': 'true',
			'timezone': 'auto',
		}

		async with aiohttp.ClientSession() as session:
			try:
				async with session.get(self.base_url, params=params) as resp:
					if resp.status != 200:
						print(await resp.text())
						return None
					data = await resp.json()
			except Exception as e:
				print(e)
				return None

		await self.cache.set(key, json.dumps(data), ex=300)

		return data

	def format_weather(self, data: dict, units: str) -> str:
		"""Форматирование ответа"""
		if not data or 'current_weather' not in data:
			return '❌ Не удалось получить данные о погоде.'

		cw = data['current_weather']
		temp = cw['temperature']
		wind = cw.get('windspeed')
		unit_symbol = '°C'

		if units == 'fahrenheit':  # Конвертация в Фаренгейты
			temp = temp * 9 / 5 + 32
			unit_symbol = '°F'

		return (
			f'🌡 Температура: {temp:.1f}{unit_symbol}\n'
			f'💨 Ветер: {wind} м/с\n'
			f'⏱ Время обновления: {cw["time"]}'
		)
