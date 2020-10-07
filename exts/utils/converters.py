import discord
from discord.ext import commands

class convert_this(commands.Converter):
	async def convert(self, ctx, arg):
		try:
			return int(arg)
		except:
			if arg.lower() in ['max', 'all']:
				return arg.lower()
			else:
				raise commands.BadArgument("user didn't input keyword (max or all) or an int")

class BadCoinSide(commands.BadArgument):
	pass

class TooManyDice(commands.BadArgument):
	pass

class CoinSide(commands.Converter):
	async def convert(self, ctx, arg):
		side = arg.lower()
		if side.startswith('h'):
			side = ['heads', '<a:heads:733951391361663027>']
			return side
		elif side.startswith('t'):
			side = ['tails', '<a:tails:733951392624148500>']
			return side
		else:
			raise BadcoinSide()

class Dices(commands.Converter):
	async def convert(self, ctx, arg):
		try:
			dices = int(arg)
		except ValueError as err:
			raise err
		if dices > 10:
			raise TooManyDice()
		return dices