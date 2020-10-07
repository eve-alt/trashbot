import discord
from discord.ext import commands

import random

class MyHelpCommand(commands.HelpCommand):

	async def send_bot_help(self, mapping):
		ctx = self.context
		bot = ctx.bot
		"""def paginate(text: str):
			last = 0
			pages = []
			for curr in range(0, len(text)):
				if curr % 1980 == 0:
					pages.append(text[last:curr])
					last = curr
					appd_index = curr
			if appd_index != len(text)-1:
				pages.append(text[last:curr])
			return list(filter(lambda a: a != '', pages))


		try:
			out = await ctx.send(f'```py\n{mapping.items()}\n```')
		except:
			paginated_text = paginate(str(mapping.items()))
			for page in paginated_text:
				if page == paginated_text[-1]:
					out = await ctx.send(f'```py\n{page}\n```')
					break
				await ctx.send(f'```py\n{page}\n```')"""
		"""e = discord.Embed(color=discord.Color(0x2f3136), title=f"\U00002139\U0000fe0f Help", description=f"You can `{ctx.prefix}help <command>` for more information on a command.\nYou can also `{ctx.prefix}help <category>` for more info on a category.")
		mypp = []
		for cog, commands in mapping.items():
			for command in commands:
				mypp.append(f"`{ctx.prefix}{command.name}`")
			e.add_field(name=f"{str(cog.qualified_name).title()}", value=", ".join(mypp), inline=False)
		e.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url_as(static_format='png'))
		await ctx.send(embed=e)"""
		e = discord.Embed(color=discord.Color(0x2f3136), title="Here are my commands!")
		e.description = f'```md\n- Arguments are the words you see next to a command.\n- Arguments with "=" are optional.\n- Arguments without "=" are required, same for arguments inside a "<>".\n\nFor command help:\n• {ctx.prefix}help <command>\n• {ctx.prefix}help <group/parent> <subcommand>\nFor category help:\n• {ctx.prefix}help <category/cog>\n```**[Support Server](https://discord.gg/zQ9KT2X) | [Invite Me](https://discord.com/oauth2/authorize?client_id=733645780925284413&permissions=201845825&scope=bot)**'
		e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url_as(static_format='png'))
		cogs = bot.cogs
		skip_field = ["eval", "help"]
		for x in cogs:
			mypp = []
			if str(x).lower() in skip_field:
				pass
			else:
				cog = bot.get_cog(f'{x}')
				commands = cog.get_commands()
				for y in commands:
					if y.hidden:
						pass
					else:
						mypp.append(f"`{ctx.prefix}{y.name}`")
				e.add_field(name=f"{str(x).title()}", value=", ".join(mypp), inline=False)
		await ctx.send(embed=e)

	async def send_cog_help(self, cog):
		ctx = self.context
		gay = ["""
░█████╗░██╗░░░██╗████████╗██╗███████╗
██╔══██╗██║░░░██║╚══██╔══╝██║██╔════╝
██║░░╚═╝██║░░░██║░░░██║░░░██║█████╗░░
██║░░██╗██║░░░██║░░░██║░░░██║██╔══╝░░
╚█████╔╝╚██████╔╝░░░██║░░░██║███████╗
░╚════╝░░╚═════╝░░░░╚═╝░░░╚═╝╚══════╝""", """
░██████╗░░█████╗░██╗░░░██╗
██╔════╝░██╔══██╗╚██╗░██╔╝
██║░░██╗░███████║░╚████╔╝░
██║░░╚██╗██╔══██║░░╚██╔╝░░
╚██████╔╝██║░░██║░░░██║░░░
░╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░""", """
██╗░░██╗██╗
██║░░██║██║
███████║██║
██╔══██║██║
██║░░██║██║
╚═╝░░╚═╝╚═╝"""]
		e = discord.Embed(color=discord.Color(0x2f3136), description=f"```{random.choice(gay)}\n\nYou can do {ctx.prefix}help <command> for more information on a command.```")
		e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url_as(static_format='png'))
		commands = cog.get_commands()
		mysmolpp = []
		for command in commands:
			mysmolpp.append(f"`{ctx.prefix}{command.name}`")
		e.add_field(name=f"**{str(cog.qualified_name).title()}**", value=", ".join(mysmolpp), inline=False)
		await ctx.send(embed=e)

	async def send_command_help(self, command):
		ctx = self.context
		if command.parent is None:
			e = discord.Embed(color=discord.Color(0x2f3136), description=f"```md\n{ctx.prefix}{command.name} {command.signature}```\n{command.help}")
			e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url_as(static_format='png'))
			if str(command.aliases) == "[]":
				pass
			else:
				aliakek = []
				for x in command.aliases:
					aliakek.append(f"`{ctx.prefix}{x}`")
				e.add_field(name="*Aliases:*", value=f", ".join(aliakek))
			await ctx.send(embed=e)
		else:
			e = discord.Embed(color=discord.Color(0x2f3136), description=f"```md\n{ctx.prefix}{command.parent} {command.name} {command.signature}```\n{command.help}")
			e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url_as(static_format='png'))
			if str(command.aliases) == "[]":
				pass
			else:
				aliakek = []
				for x in command.aliases:
					aliakek.append(f"`{ctx.prefix}{command.parent} {x}`")
				e.add_field(name="*Aliases:*", value=f", ".join(aliakek))
			await ctx.send(embed=e)

	async def send_group_help(self, group):
		ctx = self.context
		cmds = group.commands
		pp = []
		for x in cmds:
			pp.append(f"`• {x.name}`")
		hehe = "\n".join(pp)
		e = discord.Embed(color=discord.Color(0x2f3136), description=f"```md\n{ctx.prefix}{group.name} {group.signature}\n\nYou can do {ctx.prefix}help {group.name} <subcommand> for more information on a command.```\n{group.short_doc}")
		e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url_as(static_format='png'))
		e.add_field(name="**Subcommands:**", value=f"{hehe}")
		await ctx.send(embed=e)


class Help(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.client._original_help_command = client.help_command
		client.help_command = MyHelpCommand()
		client.help_command.cog = self

	def cog_unload(self):
		self.client.help_command = self.client._original_help_command

def setup(client):
	client.add_cog(Help(client))