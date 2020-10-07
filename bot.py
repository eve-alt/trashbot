import discord
from discord.ext import commands

import json, logging, datetime, aiohttp, traceback, sys, dbl
from exts.utils.formats import read_file
from pymongo import MongoClient as mc


def get_pre(bot, message):
	prefix = read_file('prefs.json')
	return [f'{prefix[str(message.guild.id)]} ',f'{prefix[str(message.guild.id)]}']

log = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True

class TrashBot(commands.AutoShardedBot):
	def __init__(self):
		super().__init__(
			command_prefix=get_pre,
			owner_ids={745315772943040563, 342361263768207360, 699882706850414622},
			case_insensitive=True,
			activity=discord.Activity(type=discord.ActivityType.competing, name='top.gg! Vote now!'),
			intents=intents
		)

		self.config = read_file('configvars.json')
		self.session = aiohttp.ClientSession(loop=self.loop)
		self.db = mc(self.config['mongo_url'])['discord']
		self.bonus_time = 0
		self.dblpy = dbl.DBLClient(
						self, 
						self.config['dbl'], 
						webhook_path='/dblwebhook',
						webhook_auth=self.config['dbl'],
						webhook_port=5000
					)

		exts = [
			'exts.economy',
			'exts.dblcog',
			'jishaku'
		]

		for ext in exts:
			try:
				self.load_extension(f'{ext}')
				print(f'Booted extension `{ext}`')
			except Exception as error:
				print(f'Extension `{ext}` couldn\'t be loaded: {error}')

	async def on_ready(self):
		if not hasattr(self, 'uptime'):
			self.uptime = datetime.datetime.utcnow()

		print(f'Logged in as {self.user}: (ID: {self.user.id})')

	async def on_guild_join(self, guild):
		prefix = read_file('prefs.json')
		prefix[f'{guild.id}'] = 'zz'
		with open('prefs.json', 'w') as f:
			json.dump(prefix, f, indent=4)

	async def on_guild_remove(self, guild):
		prefix = read_file('prefs.json')
		prefix.pop(f'{guild.id}')
		with open('prefs.json', 'w') as f:
			json.dump(prefix, f, indent=4)

	async def on_commands_error(self, ctx, error):
		if isinstance(error, commands.NoPrivateMessage):
			await ctx.author.send('Can\'t use this command in dms.')
		elif isinstance(error, commands.DisabledCommand):
			await ctx.author.send('This command is disabled.')
		elif isinstance(error, commands.CommandInvokeError):
			original = error.original
			if not isinstance(original, discord.HTTPException):
				print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
				traceback.print_tb(original.__traceback__)
				print(f'{original.__class__.__name__}: {original}', file=sys.stderr)

	async def close(self):
		await super().close()
		await self.session.close()
		await self.dblpy.close()

	def run(self):
		super().run(self.config['tkn'])