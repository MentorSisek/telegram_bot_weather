from skuf import BaseSettings


class Settings(BaseSettings):
	bot_token: str
	redis_url: str

	@property
	def redis_url_telegram(self):
		return self.redis_url + '/0'

	@property
	def redis_url_openmeteo(self):
		return self.redis_url + '/1'


settings = Settings()
