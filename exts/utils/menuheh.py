from discord.ext import menus

class MySource(menus.ListPageSource):
	def __init__(self, data):
		super().__init__(data, per_page=4)

	async def format_page(self, menu, entries):
		offset = menu.current_page * self.per_page
		return '\n'.join(f'{i}. {v}' for i, v in enumerate(entries, start=offset))