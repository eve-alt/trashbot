import discord
from discord.ext import commands

class NotRegistered(commands.CheckFailure):
	"""Exception raised when user is not registered."""
	pass

class UserNotRegistered(commands.CheckFailure):
	"""Exception raised when the user mentioned is not registered."""
	pass

class AlreadyRegistered(commands.CheckFailure):
	"""Exception raised when the user is already registered."""
	pass




class NoPet(commands.CheckFailure):
	"""Exception raised when user doesn't have a pet"""
	pass

class UserNoPet(commands.CheckFailure):
	"""Exception raised when user mentioned doesn't have a pet."""
	pass

class PetNotFound(commands.CheckFailure):
	"""Exception raised when a pet is not found."""
	pass

class AlreadyHasPet(commands.CheckFailure):
	"""Exception raised when the user already has a pet."""
	pass




class NotMarried(commands.CheckFailure):
	"""Exception raised when the user is not married."""
	pass

class AlreadyMarried(commands.CheckFailure):
	"""Exception raised when the user is already married."""
	pass

class UserAlreadyMarried(commands.CheckFailure):
	"""Exception raised when the user is trying to marry someone married."""
	pass




class Unemployed(commands.CheckFailure):
	"""Exception raised when the user doesn't have a job."""
	pass

class Employed(commands.CheckFailure):
	"""Exception raised when the user has a job."""
	pass




class NotCEO(commands.CheckFailure):
	"""Exception raised when the user isn't a CEO."""
	pass

class AlreadyCEO(commands.CheckFailure):
	"""Exception raised when the user is already a CEO."""
	pass




class NotEnoughBal(commands.CheckFailure):
	"""Exception raised when the user don't have enough bal."""
	pass

class UserNotEnoughBal(commands.CheckFailure):
	"""Exception raised when the user mentioned doesn't have enough bal."""
	pass

class NoBal(commands.CheckFailure):
	"""Exception raised when the user doesn't have any bal."""
	pass




class NiceTry(commands.CheckFailure):
	"""Exception raised when the user tried to input amount less than 0."""
	pass

class InvalidResponse(commands.CheckFailure):
	"""Exception raised when the user's response is not valid."""
	pass

class Declined(commands.CheckFailure):
	"""Exception raised when the user got declined."""
	pass

class InvalidAmount(commands.CheckFailure):
	"""Exception raised when the user inputted invalid amount."""
	pass

class NoUserStats(commands.CheckFailure):
	"""Exception raised when the user has no stats in the database."""
	pass

class FailCommand(commands.CheckFailure):
	"""Exception raised when I want to fail the command."""
	pass

class SelfRep(commands.CheckFailure):
	"""Exception raised when user reps himself."""
	pass

class ItemNotFound(commands.CheckFailure):
	"""Exception raised when the item could not be found."""
	pass

class RequestTimedOut(commands.CheckFailure):
	"""Exception raised when a request reached its timeout without a response."""
	pass

def is_registered():
	"""Checks if the user is registered."""
	async def predicate(ctx):
		currency = ctx.bot.db['currency']
		existing = currency.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if existing:
			return True

		raise NotRegistered('nope. you\'re not registered.')

	return commands.check(predicate)

def is_not_registered():
	"""Checks if the user is not registered."""
	async def predicate(ctx):
		currency = ctx.bot.db['currency']
		existing = currency.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if not existing:
			return True

		raise AlreadyRegistered('nope. you\'re already registered. smh')

	return commands.check(predicate)

def has_pet():
	"""Checks if the user has pet."""
	async def predicate(ctx):
		userpets = ctx.bot.db['userpets']
		existingpet = userpets.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if existingpet:
			return True
		raise NoPet('u don\'t have a pet, maybe adopt one first?')

	return commands.check(predicate)

def has_no_pet():
	"""Checks if the user has no pet."""
	async def predicate(ctx):
		userpets = ctx.bot.db['userpets']
		existingpet = userpets.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if not existingpet:
			return True
		raise AlreadyHasPet('u already have a pet, smh.')

	return commands.check(predicate)

def is_married():
	"""Checks if the user is married."""
	async def predicate(ctx):
		marriage = ctx.bot.db['marriage']
		married = marriage.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if married:
			return True
		raise NotMarried('what a loner, you\'re not married.')

	return commands.check(predicate)

def is_not_married():
	"""Checks if the user is not married."""
	async def predicate(ctx):
		marriage = ctx.bot.db['marriage']
		married = marriage.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if not married:
			return True
		raise AlreadyMarried('you\'re already married. smh')

	return commands.check(predicate)

def is_employed():
	"""Checks if the user is employed."""
	async def predicate(ctx):
		userjobs = ctx.bot.db['userjobs']
		employed = userjobs.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if employed:
			return True
		raise Unemployed('u don\'t have a job. maybe apply for one first?')

	return commands.check(predicate)

def is_unemployed():
	"""Checks if the user is unemployed."""
	async def predicate(ctx):
		userjobs = ctx.bot.db['userjobs']
		employed = userjobs.find_one(
			{
				"uid":ctx.author.id
			}
		)

		if not employed:
			return True
		raise Employed('u already have a job, can you not? smh.')

	return commands.check(predicate)

def is_CEO():
	"""Checks if a user is CEO."""
	async def predicate(ctx):
		jobs = ctx.bot.db['joblist']
		owner = jobs.find_one(
			{
				"owner_id":ctx.author.id
			}
		)

		if owner:
			return True
		raise NotCEO('nope, you\'re not a CEO. gtfo')

	return commands.check(predicate)

def not_CEO():
	"""Checks if a user is not CEO."""
	async def predicate(ctx):
		jobs = ctx.bot.db['joblist']
		owner = jobs.find_one(
			{
				"owner_id":ctx.author.id
			}
		)

		if not owner:
			return True
		raise AlreadyCEO()

	return commands.check(predicate)