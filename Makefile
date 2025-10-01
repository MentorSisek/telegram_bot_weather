include .env

test:
	uv run pytest

ps:
	docker compose ps -a

up:
	docker compose up -d --build && make logs

logs:
	docker compose logs -f --tail=1000 telegram_bot

stop:
	docker compose stop

start:
	docker compose start && make logs

restart:
	docker compose restart && make logs
