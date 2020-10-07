import discord, dbl, random, datetime
from discord.ext import commands


class DBL(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db = self.bot.db
		self.usercmd = self.db['usercmd']
		self.currency = self.db['currency']
		self.dblpy = self.bot.dblpy

	async def get_the_fucking_balance(self, uid):
		u = self.currency.find_one(
			{
				'uid':uid
			}
		)
		return int(u['bal'])

	async def add_vote(self, uid, n:int):
		q = self.usercmd.find_one(
			{
				'uid':uid
			}
		)

		if q:
			try:
				votes = int(q['votes'])
			except:
				votes = 0

			self.usercmd.update_one(
				{
					'uid':uid
				},
				{
					'$set':{
						'votes':int(votes+n)
					}
				}
			)

		else:
			await self.bot.get_user(342361263768207360).send(f'user {uid} doesn\'t exist in the usercmd collection and voted.')

	async def add_vote_reward(self, uid, reward):
		bal = await self.get_the_fucking_balance(uid)
		self.currency.update_one(
			{
				'uid':uid
			},
			{
				'$set':{
					'bal':int(bal+reward)
				}
			}
		)

	async def get_user_multiplier(self, uid):
		u = self.currency.find_one(
			{
				'uid':uid
			}
		)
		return u['multiplier']

	async def post_to_feed(self, user, n):
		channel = self.bot.get_channel(756248350516445425)
		r,g,b = random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)
		e = discord.Embed(
			color=discord.Color.from_rgb(r,g,b)
		).set_author(
			name=f'{user.name} voted in top.gg and got {n}c',
			icon_url=user.avatar_url_as(static_format='png')
		)
		await channel.send(embed=e)

	async def update_last_vote(self, uid):
		t = await self.strf_time(str(datetime.datetime.utcnow()))
		self.currency.update_one(
			{
				'uid':uid
			},
			{
				'$set':{
					'lastvote':t
				}
			}
		)

	async def strf_time(self, time):
		t = str(time).split('.', 1)[0]
		return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

	@commands.Cog.listener()
	async def on_dbl_vote(self, data):
		vote_x2 = data['isWeekend']
		user = self.bot.get_user(int(data['user']))
		multi = await self.get_user_multiplier(user.id)
		n = random.randint(300, 500)
		rew = int(n+(n*multi))
		res = f'you got **{n}** multiplied by **{multi}** = **{int((n*multi)+n)}** for a total of **{rew}c**!\n*you can vote again after 12h!*\n*don\'t forget to vote on weekends, you\'ll get 2x rewards*'
		votec = 1

		if vote_x2:
			rew = int((n+(n*multi))*2)
			res = f'you got **{n}** multiplied by **{multi}** = **{int((n*multi)+n)}** and **x2** because it\'s the weekend! you got a total of **{rew}c**\n*you can vote again after 12h!*'
			votec = 2

		e = discord.Embed(
			color=discord.Color(0x2f3136),
			description=res
		)
		e.set_author(
			name=f'Thanks for voting, {user.name}!'
		)
		e.set_thumbnail(
			url='https://cdn.discordapp.com/attachments/736200150837493822/756241814591111309/upvote.png'
		)
		await self.add_vote(user.id, votec)
		await self.add_vote_reward(user.id, rew)
		await self.post_to_feed(user, rew)
		await self.update_last_vote(user.id)
		await user.send(embed=e)




	@commands.Cog.listener()
	async def on_dbl_test(self, data):
		print(data)

def setup(bot):
	bot.add_cog(DBL(bot))