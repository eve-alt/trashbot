import discord
from discord.ext import commands


class Helpers:
	def __init__(self, ctx):
		self.ctx = ctx
		self.bot = self.ctx.bot