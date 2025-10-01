from typing import Any

from redis.asyncio import Redis


class Cache:
	def __init__(self, redis_url: str | None = None):
		if redis_url:
			self.storage = Redis.from_url(redis_url, decode_responses=True)
		else:
			self.storage = {}

	async def get(self, key: str):
		if isinstance(self.storage, dict):
			return self.storage.get(key)
		return await self.storage.get(key)

	async def set(self, key: str, value: Any, ex: int | None = None):
		if isinstance(self.storage, dict):
			self.storage[key] = value
		else:
			await self.storage.set(key, value, ex=ex)
