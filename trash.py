import contextlib
import logging
import asyncio
import datetime

from bot import TrashBot
from exts.utils.formats import read_file

config = read_file('configvars.json')

@contextlib.contextmanager
def setup_logging():
	try:
		logging.getLogger('discord').setLevel(logging.INFO)
		logging.getLogger('discord.http').setLevel(logging.WARNING)

		log = logging.getLogger()
		log.setLevel(logging.INFO)
		handler = logging.FileHandler(filename='trash.log', encoding='utf-8', mode='w')
		dt_fmt = '%Y-%m-%d %H:%M:%S'
		fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
		handler.setFormatter(fmt)
		log.addHandler(handler)

		yield
	finally:
		handlers = log.handlers[:]
		for hdlr in handlers:
			hdlr.close()
			log.removeHandler(hdlr)

def run_trash():
	loop = asyncio.get_event_loop()
	log = logging.getLogger()

	bot = TrashBot()
	bot.run()

def main():
	loop = asyncio.get_event_loop()
	with setup_logging():
		run_trash()

if __name__ == '__main__':
	main()