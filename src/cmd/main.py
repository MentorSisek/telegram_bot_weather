import logging

from telegram import bot

logging.basicConfig(level=logging.INFO)


async def main():
	await bot.run()


if __name__ == '__main__':
	import asyncio

	asyncio.run(main())
