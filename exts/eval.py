import discord
from discord.ext import commands
import os
import json
import inspect
import io
import textwrap
import traceback
import aiohttp
from contextlib import redirect_stdout
import base64
import json
import pprint
import typing

async def is_moron(ctx):
	return ctx.author.id in [362632769442152448, 342361263768207360, 409415146188963840, 543692940573278208]

class eval(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def format_fields(self, mapping:typing.Mapping[str, typing.Any], field_width:typing.Optional[int]=None):
		fields = sorted(mapping.items(), key=lambda item: item[0])
		if field_width is None:
			field_width = len(max(mapping.keys(), key=len))

		out = ''

		for key, val in fields:
			if isinstance(val, dict):
				inner_width = int(field_width*1.6)
				val = '\n' + self.format_fields(val, field_width=inner_width)

			elif isinstance(val, str):
				text = textwrap.fill(val, width=100, replace_whitespace=False)
				val = textwrap.indent(text, ' '*(field_width+ len(': ')))
				val = val.lstrip()

			if key == 'color':
				val = hex(val)

			out += '{0:>{width}}: {1}\n'.format(key, val, width=field_width)
		return out.rstrip()

	@commands.command(name='eval')
	@commands.check(is_moron)
	async def _eval(self, ctx, *, body):
	
		def cleanup_code(content):
			"""Automatically removes code blocks from the code."""
			# remove ```py\n```
			if content.startswith('```') and content.endswith('```'):
				return '\n'.join(content.split('\n')[1:-1])

			# remove `foo`
			return content.strip('` \n')

		def get_syntax_error(e):
			if e.text is None:
				return f'```py\n{e.__class__.__name__}: {e}\n```'
			return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

		
		blocked_words = ['rmtree','shutil','.delete()', 'subprocess', 'history()', '("token")', "('token')",
						'aW1wb3J0IG9zCnJldHVybiBvcy5lbnZpcm9uLmdldCgndG9rZW4nKQ==', 'aW1wb3J0IG9zCnByaW50KG9zLmVudmlyb24uZ2V0KCd0b2tlbicpKQ==']
		if ctx.author.id != self.bot.owner_id:
			for x in blocked_words:
				if x in body:
					return await ctx.send('Your code contains certain blocked words.')
		env = {
			'ctx': ctx,
			'bot': self.bot,
			'channel': ctx.channel,
			'author': ctx.author,
			'guild': ctx.guild,
			'message': ctx.message,
			'source': inspect.getsource
		}

		env.update(globals())

		body = cleanup_code(body)
		stdout = io.StringIO()
		err = out = None

		to_compile = f'async def func():\n{textwrap.indent(body, "	")}'

		def paginate(text: str):
			'''Simple generator that paginates text.'''
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
			exec(to_compile, env)
		except Exception as e:
			err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
			return await ctx.message.add_reaction('\u2049')

		func = env['func']
		try:
			with redirect_stdout(stdout):
				ret = await func()
		except Exception as e:
			value = stdout.getvalue()
			err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
		else:
			value = stdout.getvalue()
			if ret is None:
				if value:
					try:
						out = await ctx.send(f'```py\n{value}\n```')
					except:
						paginated_text = paginate(value)
						for page in paginated_text:
							if page == paginated_text[-1]:
								out = await ctx.send(f'```py\n{page}\n```')
								break
							await ctx.send(f'```py\n{page}\n```')
			else:
				self.bot._last_result = ret
				try:
					out = await ctx.send(f'```py\n{value}{ret}\n```')
				except:
					paginated_text = paginate(f"{value}{ret}")
					for page in paginated_text:
						if page == paginated_text[-1]:
							out = await ctx.send(f'```py\n{page}\n```')
							break
						await ctx.send(f'```py\n{page}\n```')

		if out:
			await ctx.message.add_reaction('\u2705')	# tick
		elif err:
			await ctx.message.add_reaction('\u2049')	# x
		else:
			await ctx.message.add_reaction('\u2705')

	@commands.group(invoke_without_command=True)
	@commands.check(is_moron)
	async def raw(self, ctx, *, message:discord.Message, json:bool=False):
		raw_data = await ctx.bot.http.get_message(message.channel.id, message.id)
		paginator = commands.Paginator()
		def add_content(title:str, content:str):
			paginator.add_line(f'== {title} ==\n')
			paginator.add_line(content.replace('```', '`` `'))
			paginator.close_page()

		if message.content:
			add_content('Raw message', message.content)

		transformer = pprint.pformat if json else self.format_fields
		for field_name in ('embeds', 'attachments'):
			data = raw_data[field_name]

			if not data:
				continue

			total = len(data)
			for current, item in enumerate(data, start=1):
				title = f"Raw {field_name} ({current}/{total})"
				add_content(title, transformer(item))

		for page in paginator.pages:
			await ctx.send(page)

	@raw.command()
	@commands.check(is_moron)
	async def json(self, ctx, message:discord.Message):
		await ctx.invoke(self.raw, message=message, json=True)


def setup(bot):
	bot.add_cog(eval(bot))		