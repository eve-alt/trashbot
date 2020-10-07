import discord, random, datetime, aiohttp, asyncio, typing, humanize, math, json, os, time, secrets

from discord.ext import commands
from .utils.converters import convert_this, CoinSide, Dices
from .utils.tchecks import *
from disputils import BotEmbedPaginator
from pet import Pet

class BlackJack:
	def __init__(self, ctx, money):
		self.cards = {
			    "aspades": "<:ace_of_spades:740529654330294292>",
			    "2spades": "<:2_of_spades:740529634277326898>",
			    "3spades": "<:3_of_spades:740529640841674833>",
			    "4spades": "<:4_of_spades:740529639478263888>",
			    "5spades": "<:5_of_spades:740529644754829402>",
			    "6spades": "<:6_of_spades:740529646847787008>",
			    "7spades": "<:7_of_spades:740529647611150408>",
			    "8spades": "<:8_of_spades:740529650270339143>",
			    "9spades": "<:9_of_spades:740529650794758244>",
			    "10spades": "<:10_of_spades:740529652421886022>",
			    "jspades": "<:jack_of_spades2:740529686999990373>",
			    "qspades": "<:queen_of_spades2:740532125274734653>",
			    "kspades": "<:king_of_spades2:740529680654008401>",
			    "aclubs": "<:ace_of_hearts:740529650974851192>",
			    "2clubs": "<:2_of_hearts:740529631937036359>",
			    "3clubs": "<:3_of_hearts:740529638899712070>",
			    "4clubs": "<:4_of_hearts:740529639327399996>",
			    "5clubs": "<:5_of_hearts:740529643844534293>",
			    "6clubs": "<:6_of_hearts:740529644884852808>",
			    "7clubs": "<:7_of_hearts:740529647145713684>",
			    "8clubs": "<:8_of_hearts:740529648361799681>",
			    "9clubs": "<:9_of_hearts:740529649385209979>",
			    "10clubs": "<:10_of_hearts:740529651012862072>",
			    "jclubs": "<:jack_of_hearts2:740529689117982720>",
			    "qclubs": "<:queen_of_hearts2:740536627482591292>",
			    "kclubs": "<:king_of_hearts2:740535809358430218>",
			    "adiamonds": "<:ace_of_diamonds:740529647405498420>",
			    "2diamonds": "<:2_of_diamonds:740529630469160961>",
			    "3diamonds": "<:3_of_diamonds:740529636437524534>",
			    "4diamonds": "<:4_of_diamonds:740529636982784020>",
			    "5diamonds": "<:5_of_diamonds:740529643009998880>",
			    "6diamonds": "<:6_of_diamonds:740529645161676830>",
			    "7diamonds": "<:7_of_diamonds:740529645966852187>",
			    "8diamonds": "<:8_of_diamonds:740529648680828988>",
			    "9diamonds": "<:9_of_diamonds:740529649217437777>",
			    "10diamonds": "<:10_of_diamonds:740529650530385971>",
			    "jdiamonds": "<:jack_of_diamonds2:740529683980091414>",
			    "qdiamonds": "<:queen_of_diamonds2:740529680867655700>",
			    "kdiamonds": "<:king_of_diamonds2:740534938465599579>",
			    "ahearts": "<:ace_of_hearts:740529650974851192>",
			    "2hearts": "<:2_of_hearts:740529631937036359>",
			    "3hearts": "<:3_of_hearts:740529638899712070>",
			    "4hearts": "<:4_of_hearts:740529639327399996>",
			    "5hearts": "<:5_of_hearts:740529643844534293>",
			    "6hearts": "<:6_of_hearts:740529644884852808>",
			    "7hearts": "<:7_of_hearts:740529647145713684>",
			    "8hearts": "<:8_of_hearts:740529648361799681>",
			    "9hearts": "<:9_of_hearts:740529649385209979>",
			    "10hearts": "<:10_of_hearts:740529651012862072>",
			    "jhearts": "<:jack_of_hearts2:740529689117982720>",
			    "qhearts": "<:queen_of_hearts2:740536627482591292>",
			    "khearts": "<:king_of_hearts2:740535809358430218>"
		}
		self.prep()
		self.ctx = ctx
		self.msg = None
		self.over = False
		self.money = money
		self.doubled = False
		self.db = self.ctx.bot.db
		self.currency = self.db['currency']

	def prep(self):
		self.deck = []
		for x in ['spades', 'clubs', 'diamonds', 'hearts']:
			for y in range(2, 15):
				if y == 11:
					z = "j"
				elif y == 12:
					z = "q"
				elif y == 13:
					z = "k"
				elif y == 14:
					z = "a"
				else:
					z = str(y)
				self.deck.append((y, x, self.cards[f"{z}{x}"]))
		self.deck = self.deck*4
		random.shuffle(self.deck)

	def deal(self):
		return self.deck.pop()

	def calc_aces(self, value, aces):
		missing = 21 - value
		num_11 = 0
		num_1 = 0
		for i in range(aces):
			if missing < 11:
				num_1 += 1
				missing -= 1
			else:
				num_11 += 1
				missing -= 11
		return num_11*11+num_1

	def total(self, hand):
		value = sum([card[0] if card[0] < 11 else 10 for card in hand if card[0] != 14])
		aces = sum([1 for card in hand if card[0] == 14])
		value += self.calc_aces(value, aces)
		return value

	def has_bj(self, hand):
		return self.total(hand) == 21

	def hit(self, hand):
		card = self.deal()
		hand.append(card)
		return hand

	async def player_win(self):
		user = self.currency.find_one({"uid":self.ctx.author.id})
		self.currency.update_one({"uid":self.ctx.author.id}, {"$set":{"bal":int(user['bal']+(self.money*2))}})

	async def player_cashback(self):
		user = self.currency.find_one({"uid":self.ctx.author.id})
		self.currency.update_one({"uid":self.ctx.author.id}, {"$set":{"bal":int(user['bal']+self.money)}})

	def pretty(self, hand):
		return " ".join([card[2] for card in hand])

	async def send(self, additional=""):
		player = self.total(self.player)
		dealer = self.total(self.dealer)
		e = discord.Embed(color=discord.Color(0x2f3136))
		e.set_author(name=f"{self.ctx.author}'s BlackJack Game", icon_url=self.ctx.author.avatar_url_as(static_format='png'))
		if not self.msg:
			e.description = additional
			e.add_field(name="**Dealer**:", value=f"{self.pretty(self.dealer)}\n`Total: {dealer}`", inline=False)
			e.add_field(name="**You**:", value=f"{self.pretty(self.player)}\n`Total: {player}`", inline=False)
			e.set_footer(text=f"Bet: {self.money}c")
			self.msg = await self.ctx.send(embed=e)
		else:
			e.description = additional
			e.add_field(name="**Dealer**:", value=f"{self.pretty(self.dealer)}\n`Total: {dealer}`", inline=False)
			e.add_field(name="**You**:", value=f"{self.pretty(self.player)}\n`Total: {player}`", inline=False)
			e.set_footer(text=f"Bet: {self.money}c")
			await self.msg.edit(embed=e)

	async def run(self):
		self.player = [self.deal()]
		self.dealer = [self.deal()]
		self.player = self.hit(self.player)
		await self.send()
		self.dealer = self.hit(self.dealer)
		if self.has_bj(self.player) and self.has_bj(self.dealer):
			await self.player_cashback()
			return await self.send(additional=f"u both got bj, it's a tie. u get to keep ur `{self.money}c`")
		elif self.has_bj(self.dealer):
			return await self.send(additional=f"dealer got bj, u lose `{self.money}c`")
		elif self.has_bj(self.player):
			await self.player_win()
			return await self.send(additional=f"gz u got a blackjack, u win `{self.money*2}c`")
		else:
			pass
		await self.msg.add_reaction("\U0001f44a")
		await self.msg.add_reaction("\U0001f6d1")
		valid = ["\U0001f44a", "\U0001f6d1"]
		user = self.currency.find_one({"uid":self.ctx.author.id})
		if user['bal'] - self.money*2 >= 0:
			await self.msg.add_reaction("\U000023ec")
			valid.append("\U000023ec")
		if not self.over:
			while self.total(self.dealer) < 22 and self.total(self.player) < 22 and not self.over:
				def check(reaction, user):
					return reaction.message.id == self.msg.id and user == self.ctx.author and str(reaction.emoji) in valid
				try:
					reaction, user = await self.ctx.bot.wait_for("reaction_add", check=check, timeout=30)
				except asyncio.TimeoutError:
					return await self.ctx.send(f"blackjack timed out, i'll take ur `{self.money}c` with me, bye.")
				try:
					await self.msg.remove_reaction(reaction, user)
				except discord.Forbidden:
					pass
				if reaction.emoji == "\U0001f44a":
					if self.doubled:
						valid.append("\U0001f6d1")
						valid.remove("\U0001f44a")
						await self.msg.add_reaction("\U0001f6d1")
						await self.msg.remove_reaction("\U0001f44a", self.ctx.bot.user)
					self.player = self.hit(self.player)
					await self.send()
				elif reaction.emoji == "\U0001f6d1":
					while self.total(self.dealer) < 17:
						self.dealer = self.hit(self.dealer)
					self.over = True
				else:
					hah = self.currency.find_one({"uid":self.ctx.author.id})
					if not hah['bal'] >= self.money*2:
						return await self.ctx.send("nah, you're too poor and lost the match.")
					self.doubled = True
					self.currency.update_one({"uid":self.ctx.author.id}, {"$set":{"bal":int(hah['bal']-self.money)}})
					self.money *= 2
					valid.remove("\U000023ec")
					valid.remove("\U0001f6d1")
					await self.msg.remove_reaction("\U000023ec", self.ctx.bot.user)
					await self.msg.remove_reaction("\U0001f6d1", self.ctx.bot.user)
					await self.send(additional="u doubled ur bet in exchange for only receiving one more card")
			player = self.total(self.player)
			dealer = self.total(self.dealer)
			if player > 21:
				await self.send(additional=f"u busted, u lose `{self.money}c`")
				await asyncio.sleep(5)
				self.over = True
			elif dealer > 21:
				await self.send(additional=f"dealer busted, damn that sucks. u win `{self.money*2}c`")
				await self.player_win()
				self.over = True
			else:
				if player > dealer:
					await self.send(additional=f"gz u win `{self.money*2}c`, ur hand higher than dealer's")
					await self.player_win()
					self.over = True
				elif dealer > player:
					await self.send(additional=f"dealer's hand higher than urs, u lose `{self.money}c`")
					self.over = True
				else:
					await self.player_cashback()
					await self.send(additional=f"tie. u get to keep ur `{self.money}c`. very lucky hm")
					self.over = True

		try:
			await self.msg.clear_reactions()
		except discord.Forbidden:
			pass

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.db = self.bot.db
		self.pets = self.db["pets"]
		self.userpets = self.db["userpets"]
		self.currency = self.db["currency"]
		self.items = self.db["items"]
		self.inventory = self.db["useritems"]
		self.marriage = self.db["marriage"]
		self.usercmd = self.db["usercmd"]
		self.achievements = self.db["achievements"]
		self.titles = self.db["titles"]
		self.achieved = self.db["usertitles"]
		self.equipped = self.db["equippedtitle"]
		self.jobs = self.db["joblist"]
		self.job = self.db["jobref"]
		self.userjobs = self.db["userjobs"]
		self.equips = self.db['equips']
		self.cards = os.listdir("assets/cards")

	async def get_user_votes(self, uid):
		u = self.usercmd.find_one(
			{
				'uid':uid
			}
		)

		if not u:
			return 0

		try:
			return int(u['votes'])
		except:
			return 0

	async def get_last_vote(self, uid):
		u = self.currency.find_one(
			{
				'uid':uid
			}
		)
		try:
			return u['lastvote']
		except:
			return None

	async def next_vote(self, uid, *, kw=None):
		lastvote = await self.get_last_vote(uid)

		if lastvote is None and kw is None:
			return 'Couldn\'t find your last vote. Maybe try voting first.'
		elif lastvote is None and kw is not None:
			return 'Ready!'

		tnow = await self.format_time(str(datetime.datetime.utcnow()))
		tvote = await self.format_time(str(lastvote))
		ttt = tnow - tvote
		rmtime = datetime.timedelta(hours=12, minutes=0) - ttt
		ts = rmtime.total_seconds()
		h,m,s = int(ts//3600), int((ts%3600)//60), int(ts%60)
		res = f'`{h} hours` and `{m} minutes`' if h > 0 else f'`{m} minutes`'
		ans = f'You can vote again after {res}.' if not rmtime.days < 0 else 'You can vote again **now**!'

		if kw is not None and kw == 'cooldown':
			ans = str(rmtime) if not rmtime.days < 0 else 'Ready!'

		return ans

	async def get_user_job(self, uid):
		u = self.userjobs.find_one(
			{
				'uid':uid
			}
		)
		return u

	async def get_user_stats(self, uid):
		u = self.usercmd.find_one(
			{
				'uid':uid
			}
		)
		return u

	async def get_company_info(self, company):
		u = self.jobs.find_one(
			{
				'name':company
			}
		)
		return u

	async def get_job_info(self, cid):
		u = self.jobs.find_one(
			{
				'cid':cid
			}
		)
		return u

	async def get_precise_job_info(self, company, job):
		u = self.job.find_one(
			{
				'company':company,
				'job':job
			}
		)
		return u

	async def get_company_owner(self, uid):
		u = self.jobs.find_one(
			{
				'owner_id':uid
			}
		)
		return u

	async def get_marriage_info(self, uid):
		u = self.marriage.find_one(
			{
				'uid':uid
			}
		)
		return u

	async def get_equipped_title(self, uid):
		u = self.equipped.find_one(
			{
				'uid':uid
			}
		)
		return u

	async def get_user_titles(self, uid):
		u = self.achieved.find_one(
			{
				'uid':uid
			}
		)
		return u

	async def check_equipped_title(self, uid):
		u = self.equipped.find_one(
			{
				'uid':uid
			}
		)

		if u:
			return True
		else:
			return False

	async def get_user_title(self, uid, title):
		u = self.achieved.find_one(
			{
				'uid':uid,
				'title':title
			}
		)
		return u

	async def get_user_inventory(self, uid):
		u = self.inventory.find(
			{
				'uid':uid
			}
		)
		return u

	async def married_check(self, uid):
		u = self.marriage.find_one(
			{
				'uid':uid
			}
		)
		if u:
			return True
		else:
			return False

	async def get_item_from_inv(self, uid, sid):
		u = self.inventory.find_one(
			{
				'uid':uid,
				'sid':sid
			}
		)
		return u

	async def get_marriage_info(self, uid):
		u = self.marriage.find_one(
			{
				'uid':uid
			}
		)
		return u

	async def get_ring(self, uid, ring):
		u = self.inventory.find_one(
			{
				'uid':uid,
				'itemtype':'ring',
				'sid':ring
			}
		)
		return u

	async def get_item_info(self, itemtype, sid):
		u = self.items.find_one(
			{
				'itemtype':itemtype,
				'sid':sid
			}
		)
		return u

	async def get_pet_info(self, uid):
		u = self.userpets.find_one(
			{
				'uid':uid
			}
		)
		return u

	async def determine_nickname(self, petdata):
		try:
			nickname = petdata['petnick']
		except TypeError:
			nickname = 'none'

		if nickname == 'none':
			nickname = str(petdata['petname']).title()

		return nickname

	async def starting_item_giver(self):
		fuck_me = [
			'accessory_left',
			'accessory_right',
			'armor',
			'boots',
			'helm',
			'mask',
			'mouth',
			'robe',
			'weapon'
		]

		all_equips = self.equips.find({})
		data = {}

		for i,y in enumerate(fuck_me):
			if y.startswith('acc'):
				y = 'accessory'
			item = self.equips.find_one(
				{
					'type':y
				}
			)[
				'item'
			]
			q = fuck_me[i]
			data[q] = item

		return data

	def add_empty_field(self, e:discord.Embed, x:int):
		for field in range(x):
			e.add_field(
				name='\u200b',
				value='\u200b'
			)
		return e

	async def getPercent(self, n1, n2):
		return int(n1/n2*100)

	async def getBar(self, percentage):
		s_full = "<:sf:730308838364020757>"
		s_empty = "<:se:730308837915230327>"
		m_full = "<:mf:730308836812128276>"
		m_empty = "<:me:730308837688606750>"
		e_full = "<:ef:730310208773160980>"
		e_empty = "<:ee:730310211285286935>"
		bar = []
		percentage = percentage//10
		for i,x in enumerate(range(percentage)):
			if percentage >= 1:
				if i == 0:
					bar.append(s_full)
				elif i == 9:
					bar.append(e_full)
				else:
					bar.append(m_full)
			else:
				if i == 0:
					bar.append(s_empty)
				elif i == 9:
					bar.append(e_empty)
				else:
					bar.append(m_empty)
		for x in range(1, 11):
			if len(bar) < 10:
				if len(bar) == 9:
					bar.append(e_empty)
				elif len(bar) == 0:
					bar.append(s_empty)
				else:
					bar.append(m_empty)
		return ''.join(bar)

	async def addTotalGambled(self, ctx, add):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})

		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})

			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalgambled":int(existingstats['totalgambled']+add)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalgambled":int(add)}})
			
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, "totalgambled":int(add)})

		else:
			pass

	async def addTotalGambledLoss(self, ctx, add):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})

		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})

			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalgambledloss":int(existingstats['totalgambledloss']+add)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalgambledloss":int(add)}})
			
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, "totalgambledloss":int(add)})

		else:
			pass

	async def cmdUsageAdd(self, ctx):
		existing = self.usercmd.find_one({"uid":ctx.author.id})
		if existing:
			try:
				self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{f"{ctx.command.name}":existing[f"{ctx.command.name}"]+1}})
			except KeyError:
				self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{f"{ctx.command.name}":1}})
		else:
			self.usercmd.insert_one({"uid":ctx.author.id, f"{ctx.command.name}":1})

	async def achievementChecker(self, ctx, findreqcount):
		findachievement = self.achievements.find_one({"name":ctx.command.name})
		if findachievement:
			finduser = self.usercmd.find_one({"uid":ctx.author.id})
			if finduser:
				if finduser[f"{findreqcount}"] >= findachievement["reqcount"]:
					await self.achievementGiver(ctx, findachievement['title'])
				else:
					pass
			else:
				pass
		else:
			pass

	async def achievementGiver(self, ctx, title):
		existingachievement = self.achieved.find_one({"uid":ctx.author.id, "title":title})
		if not existingachievement:
			findtitle = self.titles.find_one({"title":title})
			if findtitle:
				self.achieved.insert_one({"uid":ctx.author.id, 
										"title":findtitle['title'], 
										"icon":findtitle['icon'], 
										"bonus":findtitle['bonus']})
				await ctx.send(f"grats {ctx.author.mention}, u received the {findtitle['title'].title()} title. do `{ctx.prefix}title list` to check your titles.")
			else:
				pass
		else:
			pass

	async def lastDaily(self, user):
		u = self.currency.find_one({"uid":user.id})
		return u['lastdaily']

	async def lastRep(self, user):
		u = self.currency.find_one({"uid":user.id})
		try:
			return u['lastrep']
		except KeyError:
			fek = "2020-07-14 08:58:01.925721"
			rmv = str(fek).split('.', 1)[0]
			lastrep = datetime.datetime.strptime(rmv, "%Y-%m-%d %H:%M:%S")
			self.currency.update_one({"uid":user.id}, {"$set":{"lastrep":lastrep}})
			newu = self.currency.find_one({"uid":user.id})
			return newu['lastrep']

	async def format_time(self, time:str):
		time1 = str(time).split('.', 1)[0]
		return datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")

	async def dailyStreak(self, user):
		u = self.currency.find_one({"uid":user.id})
		return u['dailystreak']


	async def multiplier(self, user):
		u = self.currency.find_one({"uid":user.id})
		return u['multiplier']

	async def dailyChecker(self, user):
		try:
			lastd = await self.lastDaily(user)
			time = datetime.datetime.utcnow()
			time1 = str(time).split('.', 1)[0]
			todayd = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
			formula = todayd - lastd
			getstreak = await self.dailyStreak(user)
			getmulti = await self.multiplier(user)
			multi = getmulti-(getstreak*0.01)
			if formula.days >= 2:
				self.currency.update_one({"uid":user.id}, {"$set":{"dailystreak":0}})
				self.currency.update_one({"uid":user.id}, {"$set":{"multiplier":round(multi, 2)}})
			else:
				pass
		except:
			pass

	async def addTotalBalGiven(self, ctx, add):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})
		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})
			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalbalgiven":int(existingstats['totalbalgiven']+add)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalbalgiven":int(add)}})
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, "totalbalgiven":int(add)})
		else:
			pass

	async def addTotalWorkH(self, ctx):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})
		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})
			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalworkh":int(existingstats['totalworkh']+1)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalworkh":1}})
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, "totalworkh":1})
		else:
			pass

	async def addTotalRepGiven(self, ctx, add):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})
		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})
			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalrepgiven":int(existingstats['totalrepgiven']+add)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalrepgiven":int(add)}})
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, "totalrepgiven":int(add)})
		else:
			pass

	async def addTotalSpent(self, ctx, add):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})
		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})
			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalspent":int(existingstats['totalspent']+add)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalspent":int(add)}})
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, "totalbal":int(add)})
		else:
			pass

	async def addTotalBal(self, ctx, add):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})
		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})
			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalbal":int(existingstats['totalbal']+add)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, {"$set":{"totalbal":int(add)}})
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, "totalbal":int(add)})
		else:
			pass

	async def exists(self, kek):
		existing = self.currency.find_one({"uid":kek.author.id})
		if existing:
			await self.dailyChecker(kek.author)
		else:
			pass

	async def addTotalItemGiven(self, ctx, add):
		existingcurrency = self.currency.find_one({"uid":ctx.author.id})
		if existingcurrency:
			existingstats = self.usercmd.find_one({"uid":ctx.author.id})
			if existingstats:
				try:
					self.usercmd.update_one({"uid":ctx.author.id}, 
											{"$set":{"totalitemgiven":int(existingstats['totalitemgiven']+add)}})
				except KeyError:
					self.usercmd.update_one({"uid":ctx.author.id}, 
											{"$set":{"totalitemgiven":int(add)}})
			else:
				self.usercmd.insert_one({"uid":ctx.author.id, 
										"totalitemgiven":int(add)})
		else:
			pass

	async def determine_sp_added(self, level):
		return int((level//5)+3)

	async def level_up(self, user, channel, exp):
		existingpet = self.userpets.find_one({"uid":user.id})
		ch = self.bot.get_channel(channel)
		experience = existingpet["exp"]
		lvl_start = existingpet["level"]
		pet = ""
		if existingpet['petnick'] == "none":
			pet += existingpet['petname']
		else:
			pet += existingpet['petnick']
		lvl_end = int(experience ** (1/4))

		if lvl_start < lvl_end:
			await ch.send(f"""wow {user.mention}?? u got {exp}xp and u finally managed to level up ur "{pet}". it's now level {lvl_end}. not impressed tho, you're still dumb asf.""")
			data1 = {"uid":user.id}
			data2 = {"$set":{"level":lvl_end}}
			self.userpets.update_one(data1,data2)
			oldsp = existingpet['statpoints']
			addsp = await self.determine_sp_added(lvl_end)
			newsp = oldsp + addsp
			q = {"uid":user.id}
			q1 = {"$set":{"statpoints":newsp}}
			self.userpets.update_one(q, q1)
			self.userpets.update_one(q, {"$set":{"hp":int(existingpet['hp']+5)}})
		else:
			await ch.send(f"""u trained ur "{pet}" and it got `{exp}xp`.""")

	async def add_experience(self, user, xp):
		existingpet = self.userpets.find_one({"uid":user.id})
		currentxp = existingpet["exp"]
		currentlvl = existingpet["level"]
		experience = currentxp + xp
		data1 = {"uid":user.id}
		data2 = {"$set":{"exp":experience}}
		self.userpets.update_one(data1,data2)

	async def xp_multi(self, level):
		if level <= 9:
			num = 1
			return num
		elif level > 9 and level < 100:
			count = int(math.log10(level))
			num = int(level//math.pow(10, count))
			return num
		elif level == 100:
			num = 10
			return num
		else:
			raise Exception("Error, someone's pet level is higher than 100.")

	async def work_rng(self, amt):
		rng = random.randint(1,1000)/10
		if rng <= 20:
			resp = "*too bad you didn't get lucky in work today. u can always try after 1h.*"
			return int(amt*1), str(resp)
		elif rng <= 40:
			resp = "*kinda lucky, ur pay got doubled.*"
			return int(amt*2), str(resp)
		elif rng <= 47.5:
			resp = "*you did a really good job today. ur pay just got multiplied by 4.*"
			return int(amt*4), str(resp)
		elif rng <= 48.5:
			resp = "*congratulations, ur boss gave you a big bonus. ur pay just got multiplied by 10.*"
			return int(amt*10), str(resp)
		else:
			resp = "*too bad you didn't get lucky in work today. u can always try after 1h.*"
			return int(amt*1), str(resp)

	async def promote(self, ctx):
		stats = self.usercmd.find_one({"uid":ctx.author.id})
		if stats:
			hasjob = self.userjobs.find_one({"uid":ctx.author.id})
			if hasjob:
				findjob = self.job.find_one({"company":hasjob['company'], "job":hasjob['job']})
				nextjob = self.job.find_one({"jobid":int(findjob['jobid']+1)})
				if nextjob:
					if stats['workh'] >= nextjob['req']:
						if hasjob['job'] == nextjob['job']:
							pass
						else:
							self.userjobs.update_one({"uid":ctx.author.id}, {"$set":{"job":nextjob['job']}})
							self.userjobs.update_one({"uid":ctx.author.id}, {"$set":{"pay1":nextjob['range1']}})
							self.userjobs.update_one({"uid":ctx.author.id}, {"$set":{"pay2":nextjob['range2']}})
							await ctx.send(f"congratz, u just got promoted. your new position is {nextjob['job']}, check `{ctx.prefix}job` to see your new work pay. \U0001f44d")
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass

	async def companyIncome(self, ctx, amount:int):
		hasjob = self.userjobs.find_one({"uid":ctx.author.id})
		if hasjob:
			company = self.jobs.find_one({"name":hasjob['company']})
			if company:
				self.jobs.update_one({"name":hasjob['company']}, {"$set":{"bal":int(company['bal']+amount)}})
			else:
				pass
		else:
			pass

	async def addLogToCompany(self, ctx, company:str, amount:int, pay:int):
		company = self.jobs.find_one({"name":company})
		if company:
			if ctx.command.name == "work":
				self.jobs.update_one({"name":company['name']}, {"$push":{"logs":f"{ctx.author.name} worked and earned {pay}. +{amount} to company bal."}})
			elif ctx.command.name == "withdraw":
				self.jobs.update_one({"name":company['name']}, {"$push":{"logs":f"{ctx.author.name} withdrew {amount} from company bal."}})
			elif ctx.command.name == 'deposit':
				self.jobs.update_one({"name":company['name']}, {"$push":{"logs":f"{ctx.author.name} deposited {amount} to company bal."}})
			else:
				pass
		else:
			pass

	async def get_balance(self, uid):
		user = self.currency.find_one({"uid":uid})
		return int(user['bal'])

	async def get_currency_info(self, uid):
		user = self.currency.find_one({'uid':uid})
		return user

	@is_registered()
	@commands.command(name='coinflip', aliases=['cflip', 'cf'], help="Gamble some of ur bal using a dumb coin that cucks all the time.")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def _cf(self, ctx, amount:typing.Optional[convert_this]=1, choice:CoinSide=['heads', '<a:heads:733951391361663027>']):
		choices = ['heads','tails', 'cuck']
		spintime = random.randint(2, 8)

		existinguser = await self.get_currency_info(ctx.author.id)

		coindict = {
			'heads':'<:nmheads:733951473880399882>', 
			'tails':'<:nmtails:733951636182925312>',
			'cuck':'<:nmcuck:733953000200077395>'
		}

		if amount in ['all', 'max']:
			if existinguser['bal'] >= 50000:
				amount = 50000
			elif existinguser['bal'] == 0:
				raise NoBal('nope, u don\'t have any bal to do that. smh')
			else:
				amount = existinguser['bal']

		if amount <= 0:
			raise NiceTry('nice try. but no, fuck off.')
		else:
			if existinguser['bal'] >= amount:
				await self.addTotalGambled(ctx, amount)
				choice, coin = choice
				result = random.choice(choices)
				m = await ctx.send(f"{ctx.author.name} flipped the coin and chose `{choice}` for `{amount}c`:\n*flipping the coin...* {coin}")
				if result == choice:
					await asyncio.sleep(spintime)
					await m.edit(content=f"welp i guess the goddess of luck favors u for now. u won `{amount*2}c`:\n*coin landed on `{result}`..* {coindict[f'{result}']}")
					
					new = await self.get_currency_info(ctx.author.id)

					self.currency.update_one(
						{
							"uid":ctx.author.id
						},
						{
							"$set":{
								"bal":int(new['bal']+(amount))
							}
						}
					)

				elif result == "cuck":
					await asyncio.sleep(spintime)
					await m.edit(content=f"HAHA the coin cucked! try again.\n*coin cucked, sorry about that...* {coindict[f'{result}']}")
				else:
					await asyncio.sleep(spintime)
					await m.edit(content=f"ha fool, your luck sucks! u just lost `{amount}c`:\n*coin landed on `{result}`..* {coindict[f'{result}']}")
					
					new = await self.get_currency_info(ctx.author.id)

					self.currency.update_one(
						{
							"uid":ctx.author.id
						},
						{
							"$set":{
								"bal":int(new['bal']-amount)
							}
						}
					)
					
					await self.addTotalGambledLoss(ctx, amount)
			else:
				raise NotEnoughBal('nah, you don\'t have enough for this. smh')

	@is_registered()
	@commands.command(name='roll', help='Roll a dice with the bot or a user. To play with bot, you can skip/ignore the `user` argument.')
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def _roll(self, ctx, user:typing.Optional[discord.Member]=None, dice:typing.Optional[Dices]=1, bet:convert_this=100):
		dices = {
			'1': '<:side1:740997009577738330>', 
			'2': '<:side2:740997013407268924>', 
			'3': '<:side3:740997009338663015>', 
			'4': '<:side4:740997009837654056>', 
			'5': '<:side5:740997009669881937>', 
			'6': '<:side6:740997009909219348>'
		}
		moving_dices = [
			"<a:die:740991240308261026>", 
			"<a:die:740991240308261026>", 
			"<a:die:740991240308261026>", 
			"<a:die:740991240308261026>", 
			"<a:die:740991240308261026>", 
			"<a:die1:740991240211791872>", 
			"<a:die1:740991240211791872>", 
			"<a:die1:740991240211791872>", 
			"<a:die1:740991240211791872>", 
			"<a:die1:740991240211791872>"
		]
		useroutput = []
		m_useroutput = []
		otheroutput = []
		m_otheroutput = []
		blank = " "
		usertotal = 0
		othertotal = 0
		result = ""

		for x in range(dice):
			randomn = random.randint(1, 6)
			usertotal += randomn
			useroutput.append(dices[f'{randomn}'])
			m_useroutput.append(random.choice(moving_dices))

		for x in range(dice):
			randomn = random.randint(1, 6)
			othertotal += randomn
			otheroutput.append(dices[f'{randomn}'])
			m_otheroutput.append(random.choice(moving_dices))

		existinguser = await self.get_currency_info(ctx.author.id)

		if bet in ['max', 'all']:
			if existinguser['bal'] >= 50000:
				bet = 50000
			elif existinguser['bal'] == 0:
				raise NoBal('stop gambling you\'re already broke as fuck.')
			else:
				bet = existinguser['bal']

		if bet <= 0:
			raise NiceTry('nice try lmfao. nope.')
		elif bet > existinguser['bal']:
			raise NotEnoughBal('no. you don\'t have enough for this.')

		if user is None:
			await self.addTotalGambled(ctx, bet)
						
			self.currency.update_one(
				{
					"uid":ctx.author.id
				},
				{
					"$set":{
						"bal":int(existinguser['bal']-bet)
					}
				}
			)
						
			if usertotal > othertotal:
				result += f"gz u won. ur total's higher than me. welp here's `{bet*2}c`"
				userbal = await self.get_balance(ctx.author.id)

				self.currency.update_one(
					{
						"uid":ctx.author.id
					},
					{
						"$set":{
							"bal":int(userbal+(bet*2))
						}
					}
				)

			elif usertotal < othertotal:
				result += f"ha, my dice total is higher than urs. thanks for the free `{bet}c`"
				await self.addTotalGambledLoss(ctx, bet)

			else:
				result += f"tie. hmmmm, you're very lucky. u get to keep your `{bet}c`."
				userbal = await self.get_balance(ctx.author.id)

				self.currency.update_one(
					{
						"uid":ctx.author.id
					},
					{
						"$set":{
							"bal":int(userbal+bet)
						}
					}
				)

			m = await ctx.send(f"**{ctx.author}'s Dice Roll Game**\nProcessing..\n\n`Me:`\n{blank.join(m_otheroutput)}\n`Rolling...`\n\n`You:`\n{blank.join(m_useroutput)}\n`Rolling...`\n\nBet: `{bet}c`")
			await asyncio.sleep(5)
			await m.edit(content=f"**{ctx.author}'s Dice Roll Game**\n{result}\n\n`Me:`\n{blank.join(otheroutput)}\n`Total: {othertotal}`\n\n`You:`\n{blank.join(useroutput)}\n`Total: {usertotal}`\n\nBet: `{bet}c`")

		else:
			existinguser2 = await self.get_currency_info(user.id)
						
			if existinguser2:

				await ctx.send(f"**{user.name}**, **{ctx.author.name}** wants to gamble `{bet}c` with you using <:side6:740997009909219348>s, do you accept?\n*respond with anything starts with `y` if you accept, and `n` if otherwise.*")
				def check(m):
					return user.id == m.author.id
				try:
					answer = await self.bot.wait_for('message', check=check, timeout=30)
				except asyncio.TimeoutError:
					raise RequestTimedOut("u ran out of time and got no response. request cancelled.")

				if answer.content.lower().startswith('y'):
					if existinguser2['bal'] >= bet:
						await self.addTotalGambled(ctx, bet)
						existingstats = self.usercmd.find_one(
							{
								"uid":user.id
							}
						)

						if existingstats:
							try:
								self.usercmd.update_one(
									{
										"uid":user.id
									}, 
									{
										"$set":{
											"totalgambled":int(existingstats['totalgambled']+bet)
										}
									}
								)
							except KeyError:
								self.usercmd.update_one(
									{
										"uid":user.id
									},
									{
										"$set":{
											"totalgambled":int(bet)
										}
									}
								)

						else:
							self.usercmd.insert_one(
								{
									"uid":user.id,
									"totalgambled":int(bet)
								}
							)

						self.currency.update_one(
							{
								"uid":ctx.author.id
							},
							{
								"$set":{
									"bal":int(existinguser['bal']-bet)
								}
							}
						)

						self.currency.update_one(
							{
								"uid":user.id
							},
							{
								"$set":{
									"bal":int(existinguser2['bal']-bet)
								}
							}
						)

						if usertotal > othertotal:
							result += f"gz {ctx.author.mention} won. their total is higher than {user.mention}. they win `{bet*2}c`"
							userbal = await self.get_balance(ctx.author.id)

							try:
								self.usercmd.update_one(
									{
										"uid":user.id
									},
									{
										"$set":{
											"totalgambledloss":int(existingstats['totalgambledloss']+bet)
										}
									}
								)

							except KeyError:
								self.usercmd.update_one(
									{
										"uid":user.id
									},
									{
										"$set":{
											"totalgambledloss":int(bet)
										}
									}
								)

							self.currency.update_one(
								{
									"uid":ctx.author.id
								},
								{
									"$set":{
										"bal":int(userbal+(bet*2))
									}
								}
							)

						elif usertotal < othertotal:
							result += f"ha, {user.mention}'s total is higher than {ctx.author.mention}'s. they win `{bet*2}c`"
							userbal = await self.get_balance(user.id)
							await self.addTotalGambledLoss(ctx, bet)
							self.currency.update_one(
								{
									"uid":user.id
								},
								{
									"$set":{
										"bal":int(userbal+(bet*2))
									}
								}
							)

						else:
							result += f"u both tied. u both get to keep your bets. hmmmm"
							authorbal = await self.get_balance(ctx.author.id)
							userbal = await self.get_balance(user.id)

							self.currency.update_one(
								{
									"uid":ctx.author.id
								},
								{
									"$set":{
										"bal":int(authorbal+bet)
									}
								}
							)

							self.currency.update_one(
								{
									"uid":user.id
								},
								{
									"$set":{
										"bal":int(userbal+bet)
									}
								}
							)

						m = await ctx.send(f"**{ctx.author} and {user}'s' Dice Roll Game**\nProcessing..\n\n`{ctx.author}`\n{blank.join(m_useroutput)}\n`Rolling...`\n\n`{user}`\n{blank.join(m_otheroutput)}\n`Rolling...`\n\nBet: `{bet}c`")
						await asyncio.sleep(5)
						await m.edit(content=f"**{ctx.author} and {user}'s' Dice Roll Game**\n{result}\n\n`{ctx.author}`\n{blank.join(useroutput)}\n`Total: {usertotal}`\n\n`{user}`\n{blank.join(otheroutput)}\n`Total: {othertotal}`\n\nBet: `{bet}c`")
					
					else:
						raise UserNotEnoughBal('nah, that person doesn\'t have enough for that.')

				elif answer.content.lower().startswith('n'):
					raise Declined(f'lmfaoo, {user.mention} literally just told {ctx.author.mention} to fuck off.')

				else:
					raise InvalidResponse('nope. that\'s not a valid response.')

			else:
				raise UserNotRegistered('that user is not registered, smh.')


	@commands.command(name="draw", help="Draws a random card.")
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def _draw(self, ctx):
		await ctx.send(file=discord.File(f"assets/cards/{secrets.choice(self.cards)}"))


	@is_registered()
	@commands.command(name="blackjack", aliases=['bj'], help="Play blackjack with the dealer.")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def _blackjack(self, ctx, amount:typing.Optional[convert_this]=500):
		existinguser = await self.get_currency_info(ctx.author.id)

		if amount in ['all', 'max']:
			if existinguser['bal'] >= 50000:
				amount = 50000
				
			else:
				amount = existinguser['bal']

		if amount <= 0:
			raise NiceTry('nice try stupid but no.')

		elif amount < 500:
			raise InvalidAmount('nope, bet should be more than `500c`.')

		else:
			if existinguser['bal'] >= amount:
				await self.addTotalGambled(ctx, amount)
				self.currency.update_one(
					{
						"uid":ctx.author.id
					},
					{
						"$set":{
							"bal":int(existinguser['bal']-amount)
						}
					}
				)

				bj = BlackJack(ctx, amount)
				await bj.run()

			else:
				raise NotEnoughBal('you don\'t have this much money.')

	@is_registered()
	@commands.command(name='progress', aliases=['pg'], help="Shows the user's progress, stats and everything.")
	async def _progress(self, ctx):
		existinguser = await self.get_currency_info(ctx.author.id)
		userstats = self.usercmd.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if userstats:
			e = discord.Embed(
				color=discord.Color(0x2f3136),
				title=f'User Stats for {ctx.author}'
			)
			e.set_thumbnail(
				url=ctx.author.avatar_url_as(static_format='png')
			)
			e.set_footer(
				text=f'{ctx.author}',
				icon_url=ctx.author.avatar_url_as(static_format='png')
			)
			e.timestamp = datetime.datetime.utcnow()
			try:
				e.add_field(
					name="**\U00002022 Total Earned Bal:**",
					value=f"```css\n{userstats['totalbal']}c```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Total Earned Bal:**",
					value=f"```css\n0c```"
				)
			try:
				e.add_field(
					name="**\U00002022 Total Spent:**",
					value=f"```css\n{userstats['totalspent']}c```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Total Spent:**",
					value=f"```css\n0c```"
				)

			e.add_field(
				name="\u200b",
				value="\u200b"
			)

			try:
				e.add_field(
					name="**\U00002022 Total Bal Gambled:**",
					value=f"```css\n{userstats['totalgambled']}c```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Total Bal Gambled:**", 
					value=f"```css\nPussy (0c)```"
				)
			try:
				e.add_field(
					name="**\U00002022 Bal Gambled Losses:**",
					value=f"```css\n{userstats['totalgambledloss']}c```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Bal Gambled Losses:**", 
					value=f"```css\nLucky (0c)```"
				)

			e.add_field(
				name="\u200b",
				value="\u200b"
			)

			try:
				e.add_field(
					name="**\U00002022 Total Bal Given:**", 
					value=f"```css\n{userstats['totalbalgiven']}c```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Total Bal Given:**", 
					value=f"```css\n0c```"
				)
			try:
				e.add_field(
					name="**\U00002022 Total Rep Given:**", 
					value=f"```css\n{userstats['totalrepgiven']} Reps```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Total Rep Given:**", 
					value=f"```css\nNo reps given. :c```"
				)

			e.add_field(
				name="\u200b",
				value="\u200b"
			)

			try:
				e.add_field(
					name="**\U00002022 Married:**", 
					value=f"```css\n{userstats['marry']} times```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Married:**", 
					value=f"```css\nVirgin (0x)```"
				)
			try:
				e.add_field(
					name="**\U00002022 Divorced:**", 
					value=f"```css\n{userstats['divorce']} times```"
				)
			except KeyError:
				e.add_field(
					name="**\U00002022 Divorced:**", 
					value=f"```css\nFaithful (0x)```"
				)

			e.add_field(
				name="\u200b",
				value="\u200b"
			)

			await ctx.send(embed=e)
		else:
			raise NoUserStats('can\'t find any userstats for you, maybe try playing it more first.')

	@is_registered()
	@commands.command(name='cooldown', aliases=['cd'], help='Shows the command cooldowns for you.')
	async def _cooldown(self, ctx):
		hasjob = self.userjobs.find_one(
			{
				'uid':ctx.author.id
			}
		)
		existinguser = await self.get_currency_info(ctx.author.id)
		today = datetime.datetime.utcnow()
		dailyt = await self.lastDaily(ctx.author)
		rept = await self.lastRep(ctx.author)

		lastdaily = await self.format_time(str(dailyt))
		lastrep = await self.format_time(str(rept))
		todaytime = await self.format_time(str(today))

		try:
			lastwork = await self.format_time(str(existinguser['lastwork']))
			fwork = datetime.timedelta(hours=0, minutes=60) - (todaytime - lastwork)

			if fwork.days < 0:
				ts = fwork.total_seconds()
				h, m, s = ts//3600, (ts%3600)//60, ts%60

				if h == 0:
					if m <= 0:
						fwork = 'Ready!'
				elif ts < 0:
					fwork = 'Ready!'

		except KeyError:
			pass

		begcd = self.bot.get_command('beg').get_cooldown_retry_after(ctx)
		traincd = self.bot.get_command('train').get_cooldown_retry_after(ctx)

		fdaily = datetime.timedelta(hours=24, minutes=0) - (todaytime - lastdaily)
		frep = datetime.timedelta(hours=24, minutes=0) - (todaytime - lastrep)
		fbeg = 'Ready!' if begcd <= 0 else humanize.naturaldelta(datetime.timedelta(seconds=begcd))
		ftrain = 'Ready!' if traincd <= 0 else humanize.naturaldelta(datetime.timedelta(seconds=traincd))

		if fdaily.days < 0:
			fdaily = 'Ready!'

		if frep.days < 0:
			frep = 'Ready!'

		heh = await self.next_vote(ctx.author.id, kw='cooldown')

		e = discord.Embed(
			color=discord.Color(0x2f3136),
			title=f'Cooldowns for {ctx.author}'
		)
		e.set_thumbnail(
			url=ctx.author.avatar_url_as(static_format='png')
		)
		e.set_footer(
			text=f'{ctx.author}',
			icon_url=ctx.author.avatar_url_as(static_format='png')
		)
		e.add_field(
			name="\U00002022 **Daily:**", 
			value=f"```prolog\n{fdaily}```",
		)
		e.add_field(
			name='\U00002022 **Beg:**',
			value=f'```prolog\n{fbeg.title()}```'
		)
		e = self.add_empty_field(e, 1)
		e.add_field(
			name="\U00002022 **Rep:**", 
			value=f"```prolog\n{frep}```"
		)
		e.add_field(
			name='\U00002022 **Train:**',
			value=f'```prolog\n{ftrain.title()}```'
		)
		e = self.add_empty_field(e, 1)
		if hasjob:
			try:
				e.add_field(
					name='\U00002022 **Work:**',
					value=f"```prolog\n{fwork}```"
				)
				e = self.add_empty_field(e, 2)
			except UnboundLocalError:
				e.add_field(
					name='\U00002022 **Work:**',
					value='```prolog\nReady!```'
				)
				e = self.add_empty_field(e, 2)
		else:
			e.add_field(
				name='\U00002022 **Work:**',
				value='```prolog\nNo job.```'
			)
			e = self.add_empty_field(e, 2)

		e.add_field(
			name='\U00002022 **Vote:**',
			value=f'```prolog\n{heh}```'
		)
		e = self.add_empty_field(e, 2)

		await ctx.send(embed=e)

	@is_registered()
	@commands.command(name='daily', help='Claim your dailies and ear multiplier by keeping your streak.')
	async def _daily(self, ctx):
		existing = await self.get_currency_info(ctx.author.id)
		c = random.randint(200, 500)
		bal = existing['bal']
		lastd = await self.lastDaily(ctx.author)
		todayd = await self.format_time(str(datetime.datetime.utcnow()))
		formula = todayd - lastd
		rmtime = datetime.timedelta(hours=24, minutes=0) - formula
		if formula.days <= 0:
			ts = rmtime.total_seconds()
			h, m = int(ts//3600), int((ts%3600)//60)
			if h == 0:
				raise FailCommand(f'smh, wait after `{m}m` before claiming daily again. greedy much?')
			else:
				raise FailCommand(f'smh, wait after `{h}h` and `{m}m` before claiming daily again. greedy much?')
		elif formula.days >= 2:
			await self.dailyChecker(ctx.author)
			getmulti = await self.multiplier(ctx.author)
			beeg = int(c*getmulti)
			totalc = int(beeg+c)
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"dailystreak":1}})
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"multiplier":round(getmulti+0.01, 2)}})
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"lastdaily":todayd}})
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"bal":bal+totalc}})
			await self.addTotalBal(ctx, totalc)
			await ctx.send(f'aw stupid u lost all ur streak, but anw here\'s `{c}c` multiplied by `{getmulti}`, so u got `{totalc}c` in total. now piss off.')
		else:
			getmulti = await self.multiplier(ctx.author)
			getstreak = await self.dailyStreak(ctx.author)
			multi = getmulti+0.01
			beeg = int(c*multi)
			balwmulti = int(c+beeg)
			bonus = balwmulti - c
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"dailystreak":getstreak+1}})
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"multiplier":round(multi, 2)}})
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"lastdaily":todayd}})
			self.currency.update_one({"uid":ctx.author.id}, {"$set":{"bal":bal+balwmulti}})
			await self.addTotalBal(ctx, balwmulti)
			await ctx.send(f'nice, u got `{c}c` multiplied by ur multiplier `(x{round(multi, 2)})` for a total of `{balwmulti}c` because of no life-ing. congratulations on claiming daily `{getstreak+1}x` time(s).')

	@is_registered()
	@commands.command(name='rep', help='Command used to give rep to people. Earn an achievement in giving a certain amount of reps.')
	async def _rep(self, ctx, user:discord.Member):
		existinguser1 = await self.get_currency_info(ctx.author.id)

		if user.id == ctx.author.id:
			raise SelfRep('u can\'t rep urself dumbo.')

		existinguser2 = await self.get_currency_info(user.id)

		if existinguser2:
			try:
				lastrep = existinguser1['lastrep']
			except KeyError:
				lastrep = await self.format_time('2020-07-14 08:58:01.925721')

			todayd = await self.format_time(str(datetime.datetime.utcnow()))
			formula = todayd - lastrep
			rmtime = datetime.timedelta(hours=24, minutes=0) - formula
			if formula.days <= 0:
				ts = rmtime.total_seconds()
				h, m = int(ts//3600), int((ts%3600)//60)
				if h == 0:
					raise FailCommand(f"try again after `{int(m)}m` before repping someone again.. smh")
				else:
					raise FailCommand(f"try again after `{int(h)}h` and `{int(m)}m` before repping someone again.. smh")
			else:
				reps = existinguser2['rep']
				self.currency.update_one(
					{
						'uid':user.id
					},
					{
						'$set':{
							'rep':reps+1
						}
					}
				)

				self.currency.update_one(
					{
						'uid':ctx.author.id
					},
					{
						'$set':{
							'lastrep':todayd
						}
					}
				)

				await self.addTotalRepGiven(ctx, 1)

				e = discord.Embed(
					color=discord.Color(0x2f3136),
					description=f"{ctx.author.name} just repped {user.name}!"
				)
				e.set_author(
					name='+1 Reputation!'
				)
				e.set_thumbnail(
					url='https://cdn.discordapp.com/attachments/705399482422132740/730223158950625460/fuk.png'
				)
				e.add_field(
					name='**invite me to servers when?**',
					value='[click here to invite me rnrn](http://trashbot.lulu.cf/invite)\nif that `^` doesn\'t work, [click me](https://discord.com/oauth2/authorize?client_id=733645780925284413&permissions=201845825&scope=bot)',
					inline=False
				)
				e.add_field(
					name='**join the stupid server when? we need suggestions!!**',
					value='[click here to join us!](http://trashbot.lulu.cf/server)\nyep, if that `^` doesnt work [click me](https://discord.gg/zQ9KT2X)',
					inline=False
				)

				await ctx.send(embed=e)
		else:
			raise UserNotRegistered('that user isn\'t registered, maybe try asking them to register first.')

	@is_not_registered()
	@commands.command(name='register', aliases=['start', 'reg'], help='Use this to register an start your journey or whatever bullshit this is.')
	async def _register(self, ctx):
		finaltime = await self.format_time(str(datetime.datetime.utcnow()))
		self.currency.insert_one(
			{
				'gid':ctx.guild.id,
				'uid':ctx.author.id,
				'uname':f'{ctx.author}',
				'bal':500,
				'bank':0,
				'lastdaily':finaltime,
				'dailystreak':1,
				'multiplier':round(0.01, 2),
				'rep':0
			}
		)

		self.usercmd.insert_one(
			{
				'uid':ctx.author.id,
				'totalbal':500,
				'totalspent':0,
				'totalbalgiven':0,
				'totalitemgiven':0,
				'totalrepgiven':0,
				'workh':0
			}
		)

		await ctx.send(f'nice. welcome to hell. prepare to get very disappointed. here\'s `500c`, use ur `{ctx.prefix}daily` command again tomorrow to get more. good luck')

	@is_registered()
	@has_no_pet()
	@commands.command(name='adopt', help='Adopt a pet. Just make sure to take care of it tho.')
	async def _adopt(self, ctx, petname):
		existinguser = await self.get_currency_info(ctx.author.id)
		petinf = self.pets.find_one(
			{
				'sid':petname
			}
		)

		data = await self.starting_item_giver()

		if petinf:
			if existinguser['bal'] >= petinf['cost']:
				self.userpets.insert_one(
					{
						'uid':ctx.author.id,
						'petname':petinf['petname'],
						'petnick':'none',
						'level':petinf['level'],
						'exp':petinf['exp'],
						'hp':petinf['health'],
						'str':petinf['str'],
						'agi':petinf['agi'],
						'int':petinf['int'],
						'vit':petinf['vit'],
						'dex':petinf['dex'],
						'luk':petinf['luk'],
						'statpoints':petinf['statp'],
						'icon':petinf['icon'],
						'url':petinf['url'],
						'desc':petinf['desc'],
						'equipments':data
					}
				)
				self.currency.update_one(
					{
						'uid':ctx.author.id
					},
					{
						'$set':{
							'bal':int(existinguser['bal']-petinf['cost'])
						}
					}
				)
				await ctx.send(content=petinf['response'])
				await self.addTotalSpent(ctx, petinf['cost'])
			else:
				raise NotEnoughBal('nah, you don\'t have enough money to adopt a pet.')
		else:
			raise PetNotFound('can\'t find that pet, u sure you inputted the right shop id?')

	@is_registered()
	@commands.group(invoke_without_command=True, name='shop', help='Use this to access the shops, see subcommands for shops.')
	async def _shop(self, ctx):
		await ctx.send(f'you have to tell me which shop you want to access, smh. is it `pets` or `rings`?\n*usage: `{ctx.prefix}shop <category>`*')

	@is_registered()
	@_shop.command(name='pets', help='Shop subcommand for pet shop.')
	async def _pets(self, ctx):
		pets = self.pets.find({})
		n = 5
		desc = []

		for i,pet in enumerate(pets):
			name = pet['petname']
			cost = pet['cost']
			desc.append(f"`{i+1}` {pet['icon']} **{name.title()}**\n**ShopID:** `{pet['sid']}`\n**Cost:** `{cost}c`\n")

		final = [desc[i*n:(i+1)*n] for i in range((len(desc)+n-1)//n)]

		embeds = [
			discord.Embed(
				title=f"**Pet Shop**",
				description="\n".join(page),
				color=discord.Color(0x2f3136)
			).set_thumbnail(
				url="https://cdn.discordapp.com/attachments/705399482422132740/728282293025898546/trash.gif"
			).add_field(
				name="\u200b",
				value=f"**To adopt: `{ctx.prefix}adopt <shopid>`**"
			).set_footer(
				text=ctx.author,
				icon_url=ctx.author.avatar_url_as(static_format='png')
			) for page in final
		]

		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run()

	@is_registered()
	@_shop.command(name='rings', help='Shop subcommand for ring shop.')
	async def _rings(self, ctx):
		rings = self.items.find(
			{
				'itemtype':'ring'
			}
		)

		n = 5
		desc = []

		for i,ring in enumerate(rings):
			desc.append(f"`{i+1}` {ring['icon']} **{ring['name'].title()}**\n**ShopID:** `{ring['sid']}`\n**Cost:** `{ring['cost']}c`")

		final = [desc[i*n:(i+1)*n] for i in range((len(desc)+n-1)//n)]

		embeds = [
			discord.Embed(
				title=f"**Ring Shop**",
				description="\n".join(page),
				color=discord.Color(0x2f3136)
			).set_thumbnail(
				url="https://cdn.discordapp.com/attachments/705399482422132740/728282293025898546/trash.gif"
			).add_field(
				name="\u200b",
				value=f"**To buy: `{ctx.prefix}buy ring <shopid>`**"
			).set_footer(
				text=ctx.author,
				icon_url=ctx.author.avatar_url_as(static_format='png')
			) for page in final
		]

		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run()

	@is_registered()
	@commands.group(invoke_without_command=True, name='buy', help='Use this to buy item from shops, see subcommands for item types.')
	async def _buy(self, ctx):
		await ctx.send('u have to tell me which item type u are trying to buy.')

	@is_registered()
	@_buy.command(name='ring', help='Buy subcommand for buying rings.')
	async def _ring(self, ctx, sid):
		existinguser = await self.get_currency_info(ctx.author.id)
		finditem = self.items.find_one(
			{
				'itemtype':'ring',
				'sid':sid
			}
		)

		if finditem:
			if existinguser['bal'] >= finditem['cost']:
				existingitem = self.inventory.find_one(
					{
						'uid':ctx.author.id,
						'itemtype':finditem['itemtype'],
						'sid':finditem['sid']
					}
				)

				if existingitem:
					q = {
						'uid':ctx.author.id,
						'itemtype':'ring',
						'sid':sid
					}
					nv = {
						'$set':{
							'quantity':int(existingitem['quantity']+1)
						}
					}
					self.inventory.update_one(q, nv)

					await ctx.send(f"{finditem['buyresp']}\n*bought 1 {finditem['icon']} {finditem['name']}, now u have {existingitem['quantity']+1} of this item.")

					lfnewb = await self.get_balance(ctx.author.id)
					q1 = {
						'uid':ctx.author.id
					}
					nb = {
						'$set':{
							'bal':int(lfnewb['bal']-finditem['cost'])
						}
					}
					self.currency.update_one(q1, nb)
					await self.addTotalSpent(ctx, finditem['cost'])
				else:
					self.inventory.insert_one(
						{
							'uid':ctx.author.id,
							'itemtype':finditem['itemtype'],
							'name':finditem['name'],
							'sid':finditem['sid'],
							'icon':finditem['icon'],
							'quantity':1
						}
					)
					await ctx.send(f"{finditem['buyresp']}\n*bought 1 {finditem['icon']} {finditem['name']}, now u have 1 of this item.*")

					lfnewb = await self.get_balance(ctx.author.id)
					q = {
						'uid':ctx.author.id
					}
					nb = {
						'$set':{
							'bal':int(lfnewb['bal']-finditem['cost'])
						}
					}
					self.currency.update_one(q, nb)
					await self.addTotalSpent(ctx, finditem['cost'])
			else:
				raise NotEnoughBal('nah, you can\'t afford that ring. smh')
		else:
			raise ItemNotFound('can\'t find that ring, maybe try inputting the right shop id.')

	@is_registered()
	@commands.command(name='bal', aliases=['cash', 'balance', 'coins', 'money'], help='Command used to check how much money u have, *u probably don\'t have any so don\'t bother checking.*')
	async def _bal(self, ctx, user:discord.Member=None):
		if user is None:
			user = ctx.author
			nem = 'ur'
		else:
			user = user
			nem = f'{user.name}\'s'

		bal = await self.get_balance(user.id)

		e = discord.Embed(
			color=discord.Color(0x2f3136),
			description=f'**{nem} stupid balance:**\n\u200b \u00a0 \u00a0 `{bal}c`'
		)
		e.set_thumbnail(
			url='https://cdn.discordapp.com/attachments/736200150837493822/754081434322468986/lul.png'
		)

		await ctx.send(embed=e)

	@is_registered()
	@has_pet()
	@commands.group(invoke_without_command=True, name='pet', help='Shows urs or someone else\'s pet level, exp, stats, and etc..')
	async def _pet(self, ctx, user:typing.Optional[discord.Member]=None):
		if user is None:
			user = ctx.author

		pet = self.userpets.find_one(
			{
				'uid':user.id
			}
		)
		level = pet['level']
		exp = pet['exp']
		exp_until = int((level+1)**4)
		prcnt = await self.getPercent(exp, exp_until)
		expbar = await self.getBar(prcnt)

		e = discord.Embed(
			color=discord.Color(0x2f3136),
			description=f'**Species:** {pet["petname"]}\n**Nickname:** {pet["petnick"]}\n**Level:** {pet["level"]}\n**EXP:** {pet["exp"]}\n{str(expbar)}\n*{pet["desc"]}*\n**STATS:**' 
		)
		e.set_author(
			name=f'{user}\'s Pet',
			icon_url=user.avatar_url_as(static_format='png')
		)
		e.add_field(
			name="HP",
			value=f"{int(pet['hp'])}",
			inline=False
		)
		e.add_field(
			name="STR",
			value=f"{pet['str']}"
		)
		e.add_field(
			name="AGI",
			value=f"{pet['agi']}"
		)
		e.add_field(
			name="INT",
			value=f"{pet['int']}"
		)
		e.add_field(
			name="VIT",
			value=f"{pet['vit']}"
		)
		e.add_field(
			name="DEX",
			value=f"{pet['dex']}"
		)
		e.add_field(
			name="LUK",
			value=f"{pet['luk']}"
		)
		e.set_thumbnail(
			url=f"{pet['url']}"
		)
		e.set_footer(
			text=f"Unallocated Statpoints: {pet['statpoints']}"
		)

		await ctx.send(embed=e)

	@is_registered()
	@has_pet()
	@_pet.command(name='disown', aliases=['abandon'], help='Command used to disown your pet if you get bored with it, u can always get a new one anyways. *as long as u can afford it.*')
	async def _disown(self, ctx):
		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		nn = await self.determine_nickname(pet)

		self.userpets.delete_one(
			{
				'uid':ctx.author.id
			}
		)

		await ctx.send(f'disowned {nn}. don\'t cry about it later, stoopid.')

	@is_registered()
	@has_pet()
	@_pet.command(name='nickname', aliases=['nick', 'nn', 'setnick'], help='Command used to change ur pet\'s nickname. If you leave the `nickname` arg empty, it\'ll reset your pet\'s nickname.')
	async def _nickname(self, ctx, *, nickname=None):
		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if nickname is None:
			if pet['petnick'] == 'none':
				raise FailCommand('ur pet already doesn\'t have a nickname, stop trying to reset nothing, smh **my head**.')

			q = {
				'uid':ctx.author.id
			}
			newnick = {
				'$set':{
					'petnick':'none'
				}
			}

			self.userpets.update_one(q, newnick)
			await ctx.send('u removed ur pet\'s nickname. smh')

		else:
			if len(nickname) > 15:
				raise FailCommand('you can\'t have more than 15 characters for your pet\'s nickname.')

			q = {
				'uid':ctx.author.id
			}
			newnick = {
				'$set':{
					'petnick':nickname
				}
			}
			self.userpets.update_one(q, newnick)
			await ctx.send(f'ew, who would nickname their {pet["petname"]} "{nickname}"? weird fuk.')


	@is_registered()
	@commands.command(name='petinfo', aliases=['pdex', 'petinf', 'pinfo'], help='Acts as a dex to pets available in the shop.')
	async def _petinfo(self, ctx, *, pet=None):
		if pet is None:
			raise FailCommand('who are u even trying to search information on? try again and tell me which pet u wanna know more about, smh.')

		pet = pet.lower()

		spet = self.pets.find_one(
			{
				'petname':pet
			}
		)

		if spet:
			e = discord.Embed(
				color=discord.Color(0x2f3136),
				title=spet['petname'].title(),
				description=f"**Base HP:** {spet['health']}\
							\n**STR:** {spet['str']}\
							\n**AGI:** {spet['agi']}\
							\n**INT:** {spet['int']}\
							\n**VIT:** {spet['vit']}\
							\n**DEX:** {spet['dex']}\
							\n**LUK:** {spet['luk']}\
							\n**Starting SP:** {spet['statp']} points\
							\n**Shop Icon:** {spet['icon']}\
							\n**Shop ID:** `{spet['sid']}`\
							\n**Price:** `{spet['cost']}c`\
							\n**Description:** *{spet['desc']}*"
			)
			e.set_author(
				name='Pet Information',
				icon_url='https://cdn.discordapp.com/attachments/705399482422132740/728282293025898546/trash.gif'
			)
			e.set_image(
				url=spet['url']
			)
			await ctx.send(embed=e)

		else:
			raise PetNotFound('u sure that pet exists? can\'t find it.')

	@commands.command(name='invite', aliases=['inv'], help='Invite the bot to ur servers, would really appreciate it.')
	async def _invite(self, ctx):
		e = discord.Embed(
			color=discord.Color(0x2f3136),
			description='[click me for my invite link rn](http://trashbot.lulu.cf)\
						\n[back-up link incase the link above doesn\'t work.](https://discord.com/oauth2/authorize?client_id=733645780925284413&permissions=201845825&scope=bot)'
		)
		await ctx.send(embed=e)

	@is_registered()
	@commands.command(name='pay', help='Command used to pay another player that is registered.')
	async def _pay(self, ctx, user:discord.Member, amount:int):
		if user.id == ctx.author.id:
			raise FailCommand('are u really that stupid?')

		if amount <= 0:
			raise FailCommand('??? what r u trying to do stupid?')

		existinguser1 = await self.get_currency_info(ctx.author.id)
		existinguser2 = await self.get_currency_info(user.id)

		if existinguser2:
			if existinguser1['bal'] >= amount:
				q1 = {
					'uid':ctx.author.id
				}
				q2 = {
					'uid':user.id
				}
				nb1 = {
					'$set':{
						'bal':int(existinguser1['bal']-amount)
					}
				}
				nb2 = {
					'$set':{
						'bal':int(existinguser2['bal']+amount)
					}
				}
				self.currency.update_one(q1,nb1)
				self.currency.update_one(q2,nb2)
				nb = await self.get_balance(ctx.author.id)
				await ctx.send(f'u paid **{user}** `{amount}c`. u now have `{nb}c` left.')
				await self.addTotalBalGiven(ctx, amount)
			else:
				raise FailCommand(f'u don\'t have `{amount}c` stoopid.')
		else:
			raise UserNotRegistered('that user isn\'t registered. maybe try asking them to register first.')

	@is_registered()
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.command(name='beg')
	async def _beg(self, ctx):
		coins = random.randint(1, 50)
		user = await self.get_currency_info(ctx.author.id)
		beeg = int(coins*user['multiplier'])
		begc = int(coins+beeg)
		bal = await self.get_balance(ctx.author.id)
		q = {
			'uid':ctx.author.id
		}
		newbal = {
			'$set':{
				'bal':int(bal+begc)
			}
		}
		self.currency.update_one(q, newbal)
		responses =[
			f"ew, ugly person, here's `{begc}c`, now get the f* away from me. ugh gross.",
			f"**sylvia#0002**: stop begging for this dick, here's `{begc}c` instead.",
			f"**Oblique#1337**: why the fuck do i see these dating app ads on youtube?\n-> *u got `{begc}c` by listening to his questions.*",
			f"**Oblique#1337**: for people that do sign language, is it rude to talk with your hands full?\n-> *u got `{begc}c` by listening to his questions.*",
			f"**Syne#0110**: GR GR GR GR GR GR GR GR GR GR GR GR GR!!\n-> *u got `{begc}c` by laughing so hard at what he said.*",
			f"**rodri#2306**: who am i? ur father? get a fucking job, here's `{begc}c` so u can start. now gtfo",
			f'**rodri#2306**: imagine if you\'re born in no mans land, r u a no lander?\n -> *u got `{begc}c` by listening to his questions.*'
		]

		await ctx.send(random.choice(responses))
		await self.addTotalBal(ctx, begc)

	@is_registered()
	@has_pet()
	@commands.command(name='train')
	@commands.cooldown(1, 120, commands.BucketType.user)
	async def _train(self, ctx):
		pet = await self.get_pet_info(ctx.author.id)

		level = pet['level']
		xp = random.randint(1, 10)
		xp = int((xp*self.bot.bonus_time)+xp)
		xpmulti = await self.xp_multi(level)
		exp = int(xp*xpmulti)
		await self.add_experience(ctx.author, exp)
		await self.level_up(ctx.author, ctx.channel.id, exp)

	@is_registered()
	@has_pet()
	@commands.group(invoke_without_command=True, name='addstat', help='Command used to add a statpoint to a stat on ur pet.')
	async def _addstat(self, ctx):
		await ctx.send(f'smh, this is not the right way to do this... u should `{ctx.prefix}{ctx.command.name} <stat> <points>`. *smh*')

	@is_registered()
	@has_pet()
	@_addstat.command(name='str')
	async def _str(self, ctx, points:int):
		if points <= 0:
			raise FailCommand('i don\'t really know what you\'re trying to achieve here stupido.')

		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if pet['statpoints'] >= points:
			q = {
				'uid':ctx.author.id
			}
			newstat = {
				'$set':{
					'str':pet['str']+points
				}
			}
			newpts = {
				'$set':{
					'statpoints':int(pet['statpoints']-points)
				}
			}
			self.userpets.update_one(q, newstat)
			self.userpets.update_one(q, newpts)
			await ctx.send(f'added `{points}` statpoints to str stat, not that it would really matter because lu\'s formula sucks.')
		else:
			raise FailCommand('u sure u can count? try again and input the right amount of points to allocate.')

	@is_registered()
	@has_pet()
	@_addstat.command(name='agi')
	async def _agi(self, ctx, points:int):
		if points <= 0:
			raise FailCommand('i don\'t really know what you\'re trying to achieve here stupido.')

		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if pet['statpoints'] >= points:
			q = {
				'uid':ctx.author.id
			}
			newstat = {
				'$set':{
					'agi':pet['agi']+points
				}
			}
			newpts = {
				'$set':{
					'statpoints':int(pet['statpoints']-points)
				}
			}
			self.userpets.update_one(q, newstat)
			self.userpets.update_one(q, newpts)
			await ctx.send(f'added `{points}` statpoints to agi stat, not that it would really matter because lu\'s formula sucks.')
		else:
			raise FailCommand('u sure u can count? try again and input the right amount of points to allocate.')

	@is_registered()
	@has_pet()
	@_addstat.command(name='int')
	async def _int(self, ctx, points:int):
		if points <= 0:
			raise FailCommand('i don\'t really know what you\'re trying to achieve here stupido.')

		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if pet['statpoints'] >= points:
			q = {
				'uid':ctx.author.id
			}
			newstat = {
				'$set':{
					'int':pet['int']+points
				}
			}
			newpts = {
				'$set':{
					'statpoints':int(pet['statpoints']-points)
				}
			}
			self.userpets.update_one(q, newstat)
			self.userpets.update_one(q, newpts)
			await ctx.send(f'added `{points}` statpoints to int stat, not that it would really matter because lu\'s formula sucks.')
		else:
			raise FailCommand('u sure u can count? try again and input the right amount of points to allocate.')

	@is_registered()
	@has_pet()
	@_addstat.command(name='vit')
	async def _vit(self, ctx, points:int):
		if points <= 0:
			raise FailCommand('i don\'t really know what you\'re trying to achieve here stupido.')

		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if pet['statpoints'] >= points:
			q = {
				'uid':ctx.author.id
			}
			newstat = {
				'$set':{
					'vit':pet['vit']+points
				}
			}
			newpts = {
				'$set':{
					'statpoints':int(pet['statpoints']-points)
				}
			}
			self.userpets.update_one(q, newstat)
			self.userpets.update_one(q, newpts)

			hp = pet['hp']
			pts_range = range(1, points+1)
			for x in pts_range:
				hp += round(hp*0.01, 2)

			newhp = {
				'$set':{
					'hp':round(hp, 2)
				}
			}

			self.userpets.update_one(q,newhp)

			await ctx.send(f'added `{points}` statpoints to vit stat, not that it would really matter because lu\'s formula sucks.')
		else:
			raise FailCommand('u sure u can count? try again and input the right amount of points to allocate.')


	@is_registered()
	@has_pet()
	@_addstat.command(name='dex')
	async def _dex(self, ctx, points:int):
		if points <= 0:
			raise FailCommand('i don\'t really know what you\'re trying to achieve here stupido.')

		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if pet['statpoints'] >= points:
			q = {
				'uid':ctx.author.id
			}
			newstat = {
				'$set':{
					'dex':pet['dex']+points
				}
			}
			newpts = {
				'$set':{
					'statpoints':int(pet['statpoints']-points)
				}
			}
			self.userpets.update_one(q, newstat)
			self.userpets.update_one(q, newpts)
			await ctx.send(f'added `{points}` statpoints to dex stat, not that it would really matter because lu\'s formula sucks.')
		else:
			raise FailCommand('u sure u can count? try again and input the right amount of points to allocate.')

	@is_registered()
	@has_pet()
	@_addstat.command(name='luk')
	async def _luk(self, ctx, points:int):
		if points <= 0:
			raise FailCommand('i don\'t really know what you\'re trying to achieve here stupido.')

		pet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)

		if pet['statpoints'] >= points:
			q = {
				'uid':ctx.author.id
			}
			newstat = {
				'$set':{
					'luk':pet['luk']+points
				}
			}
			newpts = {
				'$set':{
					'statpoints':int(pet['statpoints']-points)
				}
			}
			self.userpets.update_one(q, newstat)
			self.userpets.update_one(q, newpts)
			await ctx.send(f'added `{points}` statpoints to luk stat, not that it would really matter because lu\'s formula sucks.')
		else:
			raise FailCommand('u sure u can count? try again and input the right amount of points to allocate.')

	@is_registered()
	@has_pet()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name='duel')
	async def _duel(self, ctx, user:discord.Member):
		if ctx.author.id == user.id:
			return await ctx.send('y do u wanna fight urself? idiot.')

		if user.bot:
			return await ctx.send('y do u wanna fight a bot? stupid.')

		existinguser2 = await self.get_currency_info(user.id)

		if existinguser2:
			existingpet1 = await self.get_pet_info(ctx.author.id)
			existingpet2 = await self.get_pet_info(user.id)

			if existingpet2:
				await ctx.send(f'{user.mention}, {ctx.author.mention} challenged u to a duel. will you accept? you have 30 seconds to answer.\n*say `accept` to accept the duel request, `deny` to deny.*')

				def challenged(m):
					return m.author.id == user.id

				x = 0
				while x < 50:
					try:
						kek = await self.bot.wait_for('message', check=challenged, timeout=30.0)
					except asyncio.TimeoutError:
						raise RequestTimedOut('u ran out of time, u stupid ass.')

					if kek.content.lower() == 'accept':
						p1 = Pet(f'{ctx.author.name}', ctx.author.id)
						p2 = Pet(f'{user.name}', user.id)
						return await Pet.duel(ctx.channel, p1, p2)
					elif kek.content.lower() == 'deny':
						raise Declined(f'{ctx.author.mention} u just got declined lol.')
					else:
						x += 1
			else:
				raise UserNoPet(f'{user.mention} doesn\'t have a pet, stupid.')
		else:
			raise UserNotRegistered('they\'re not registered, ask them to register first smh.')

	@commands.command(name='ping', help='pong.')
	async def _ping(self, ctx):
		kek = f'Pong! Websocket latency is `{int(self.bot.latency*1000)}ms`.'
		m = await ctx.send(content=kek)
		resp = int((m.created_at - ctx.message.created_at).total_seconds()*1000)
		kek += f'\nResponse time is `{resp}ms`.'
		await m.edit(content=kek)

	@is_registered()
	@commands.command(name='profile', aliases=['info', 'prf'], help='Command used to show someone else\'s or your profile.')
	async def _profile(self, ctx, user:discord.User=None):
		if user is None:
			user = ctx.author

		existing = await self.get_currency_info(user.id)

		if existing:
			pet = await self.get_pet_info(user.id)
			married = await self.get_marriage_info(user.id)
			equippedtitle = await self.get_equipped_title(user.id)

			e = discord.Embed(
				color=discord.Color(0x2f3136)
			)
			e.set_author(
				name=f'{user}',
				icon_url=user.avatar_url_as(static_format='png')
			)
			e.set_thumbnail(
				url=user.avatar_url_as(static_format='png')
			)
			try:
				e.add_field(
					name=f'**\U00002022 Title** {equippedtitle["icon"]}',
					value=f'```css\n{equippedtitle["title"].title()}```',
					inline=False
				)
			except TypeError:
				pass
			e.add_field(
				name='**\U00002022 Balance**',
				value=f'```css\n{existing["bal"]}```'
			)
			e.add_field(
				name='**\U00002022 Daily Streak**',
				value=f'```css\n{existing["dailystreak"]}```'
			)
			e.add_field(
				name='\u200b',
				value='\u200b'
			)
			e.add_field(
				name='**\U00002022 Multiplier**',
				value=f'```css\n{existing["multiplier"]}```'
			)
			e.add_field(
				name='**\U00002022 Reputation**',
				value=f'```css\n{existing["rep"]} Reps```'
			)
			e.add_field(
				name='\u200b',
				value='\u200b'
			)
			try:
				e.add_field(
					name=f'**\U00002022 Married to** {married["icon"]}',
					value=f'```glsl\n{married["partner_name"]}```'
				)
			except TypeError:
				pass
			try:
				pn = await self.determine_nickname(pet)
				icon = pet['icon']
				url = pet['url']
				pname = f'{icon} [{pn}]({url})'
				e.add_field(
					name='**\U00002022 Pet**',
					value=f'\n{pname}'
				)
				e.add_field(
					name='\u200b',
					value='\u200b'
				)
			except TypeError:
				pass
			e.set_footer(
				text=f'ID: {user.id}'
			)

			await ctx.send(embed=e)

		else:
			raise UserNotRegistered('they\'re not registered stupid, ask them to register first.')

	@is_registered()
	@is_not_married()
	@commands.command(name='marry', aliases=['propose'], help='Command used to propose to someone. Ofc you\'d need a ring. U can\'t marry urself btw. Sorry x)')
	async def _marry(self, ctx, user:discord.Member, ring_sid):
		if ctx.author.id == user.id:
			return await ctx.send('nope.')

		existinguser1 = await self.get_currency_info(ctx.author.id)
		existinguser2 = await self.get_currency_info(user.id)

		married = await self.married_check(user.id)

		if existinguser2:
			if not married:
				has_ring = await self.get_ring(ctx.author.id, ring_sid.lower())

				if has_ring and has_ring['quantity'] >= 1:
					def check(m):
						return m.author.id == user.id

					item_info = await self.get_item_info('ring', ring_sid.lower())

					await ctx.send(f'**{ctx.author}** is proposing to **{user}**.\nwhat do u say about that, {user.mention}?\n*reply `yes` or `no` in 2 minutes.*\n*u can also say things like "yes i fucking do!" as long as it starts with `ye` or `no` or `na`*')

					x = 0
					while x < 50:
						try:
							answer = await self.bot.wait_for('message', check=check, timeout=120)
						except asyncio.TimeoutError:
							raise RequestTimedOut(f'u ran out of time to respond {user.mention}. maybe try again later, {ctx.author.mention}.')

						if answer.content.lower().startswith('ye'):
							finaltime = await self.format_time(str(datetime.datetime.utcnow()))

							self.marriage.insert_one(
								{
									'uid':ctx.author.id,
									'partner_name':f'{user}',
									'partner_id':user.id,
									'icon':item_info['icon'],
									'url':item_info['url'],
									'date':finaltime
								}
							)
							self.marriage.insert_one(
								{
									'uid':user.id,
									'partner_name':f'{ctx.author}',
									'partner_id':ctx.author.id,
									'icon':item_info['icon'],
									'url':item_info['url'],
									'date':finaltime
								}
							)
							q = {
								'uid':ctx.author.id,
								'itemtype':'ring',
								'sid':ring_sid.lower()
							}
							nv = {
								'$set':{
									'quantity':int(has_ring['quantity']-1)
								}
							}
							self.inventory.update_one(q, nv)

							return await ctx.send(f'{item_info["icon"]} congratulations! {ctx.author.mention} and {user.mention} are now married! congratulate them u dumfoos!! >:c')

						elif answer.content.lower().startswith(('no', 'na')):
							raise Declined(f'oof, **{ctx.author.name}**\'s proposal just got declined.')

						else:
							x += 1

				else:
					raise FailCommand('either u don\'t have the ring or you don\'t have enough of that ring or the ring doesn\'t exist. u need to have atleast `1` of it, smh')

			else:
				raise UserAlreadyMarried('mmmm, i see. u like it like that? they\'re already married to someone. sorry but no, third party isn\'t allowed here.')

		else:
			raise UserNotRegistered('ask them to register first before trying to marry them, smh.')



	@is_registered()
	@is_married()
	@commands.command(name='divorce', aliases=['breakup', 'annul'], help='Command used to divorce with your partner if u get bored with them or wanna remarry.\nJust a warning tho, divorcing someone costs 75% of what your ring costs, so be careful in marrying someone.')
	async def _divorce(self, ctx):
		existinguser = await self.get_currency_info(ctx.author.id)
		m_inf = await self.get_marriage_info(ctx.author.id)
		cost = int(
			self.items.find_one(
				{
					'url':m_inf['url']
				}
			)['cost']*0.75
		)

		if existinguser['bal'] >= cost:
			raise NotEnoughBal(f'nah, u don\'t have enough balance to divorce. u need `{cost}c` for that.')

		await ctx.send(f'u sure u wanna get divorced? u ain\'t gonna find someone like **{m_inf["partner_name"]}** again. it will also cost you `{cost}c`')

		def check(m):
			return m.author.id == ctx.author.id

		try:
			answer = await self.bot.wait_for('message', check=check, timeout=120)
		except asyncio.TimeoutError:
			raise RequestTimedOut('request timed out, maybe try responding before the time runs out?')

		if answer.content.lower().startswith('ye'):
			self.marriage.delete_one(
				{
					'uid':ctx.author.id
				}
			)
			self.marriage.delete_one(
				{
					'uid':m_inf['partner_id']
				}
			)
			self.currency.update_one(
				{
					'uid':ctx.author.id
				},
				{
					'$set':{
						'bal':int(existinguser['bal']-cost)
					}
				}
			)

			await ctx.send('nice, you\'re single again. congratulations.')

		elif answer.content.lower().startswith(('no', 'na')):
			raise FailCommand('make up ur goddamn mind, stop bothering me when u don\'t really have anything good to say. smh')

		else:
			raise InvalidResponse('that\'s not a valid response, smh.')

	@is_registered()
	@is_married()
	@commands.command(name='marriage', aliases=['partner'], help='Command used to show who you\'re married to and to see how many days you have been married with them.')
	async def _marriage(self, ctx):
		married = await self.get_marriage_info(ctx.author.id)
		finaltime = await self.format_time(str(datetime.datetime.utcnow()))
		mdate = married['date']
		monthname = mdate.strftime('%B')
		formula = finaltime - mdate
		age = int(formula.days)
		name = str(married['partner_name']).split('#')[0]
		e = discord.Embed(
			color=discord.Color(0x2f3136),
			description=f'You two are happily `(?)` married since:\n**{monthname} {mdate.day}, {mdate.year}** (**{age}** days.)'
		)
		e.set_author(
			name=f'{ctx.author.name.title()} you are married to {name.title()}!',
			icon_url=ctx.author.avatar_url_as(static_format='png')
		)
		e.set_thumbnail(
			url=married['url']
		)

		await ctx.send(embed=e)

	@is_registered()
	@commands.command(name='inventory', aliases=['i', 'storage'], help='Command used to show your itmes in your inventory.')
	async def _inventory(self, ctx):
		inv = await self.get_user_inventory(ctx.author.id)

		try:
			n = 5
			op = []

			for item in inv:
				itemtype = item['itemtype']
				name = item['name']
				quantity = item['quantity']
				sid = item['sid']
				icon = item['icon']
				lfitem = await self.get_item_info(itemtype, sid)
				sellprice = int(lfitem['cost']*0.6)

				if quantity <= 0:
					pass

				else:
					op.append(f'**Type:** `{itemtype.title()}`\n{icon} `{name.title()}` **x{quantity}**\n**Sell ID:** `{sid}`\n**Sell Price:** `{sellprice}c`\n')

			final = [op[i*n:(i+1)*n] for i in range((len(op)+n-1)//n)]
			embeds = [
				discord.Embed(
					color=discord.Color(0x2f3136),
					description='\n'.join(page)
				).set_thumbnail(
					url='https://cdn.discordapp.com/attachments/705399482422132740/730927041796374538/inv.gif'
				).set_author(
					name=f'{ctx.author.name.title()}\'s Inventory',
					icon_url=ctx.author.avatar_url_as(static_format='png')
				).set_footer(
					text=f'User ID: {ctx.author.id}'
				) for page in final
			]

			paginator = BotEmbedPaginator(ctx, embeds)
			await paginator.run()

		except:
			return await ctx.send('no items in inventory..')

	@is_registered()
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.command(name='sell', help='Command used to sell your items in ur inventory for 60% of their original price.')
	async def _sell(self, ctx, sid, amount:convert_this=1):
		selling = await self.get_item_from_inv(ctx.author.id, sid.lower())

		if selling['quantity'] <= 0:
			raise FailCommand('u don\'t have that item?? maybe try checking ur inventory again.')

		if amount <= 0:
			raise FailCommand('?? tryna sell something non existent??')

		if amount in ['max', 'all']:
			amount = selling['quantity']

		if selling['quantity'] >= amount:
			finditem = await self.get_item_info(selling['itemtype'], selling['sid'])
			sellprice = int(finditem['cost']*0.6)
			lfnewb = await self.get_currency_info(ctx.author.id)
			self.currency.update_one(
				{
					'uid':ctx.author.id
				},
				{
					'$set':{
						'bal':int(lfnewb['bal']+sellprice)
					}
				}
			)
			self.inventory.update_one(
				{
					'uid':ctx.author.id,
					'sid':sid.lower()
				},
				{
					'$set':{
						'quantity':int(selling['quantity']-amount)
					}
				}
			)

			await ctx.send(f'successfully sold **{amount}x {selling["icon"]} {selling["name"]}** for `{sellprice}c`.')

		else:
			raise FailCommand('u don\'t have that amount of item on ur inventory???')

	@is_registered()
	@commands.group(invoke_without_command=True, name='title', help='Parent command for title-related commands. See subcommands for more info.')
	async def _title(self, ctx):
		raise FailCommand('smfh, it\'s either you want to `equip` a title, or `unequip` a title, or see the `list` of your titles, or `dir` to see all achievable titles.')

	@is_registered()
	@_title.command(name='list', help='Shows your titles achieved.')
	async def _list(self, ctx):
		try:
			achieved = await self.get_user_titles(ctx.author.id)
			n = 5
			op = []

			for x in achieved:
				tname = x['title']
				ticon = x['icon']
				tmulti = x['bonus']
				op.append(f'**Title Name:** {tname.title()} {ticon}\n**Bonus Multiplier:** x{tmulti}\n')

			final = [op[i*n:(i+1)*n] for i in range((len(op)+n-1)//n)]
			embeds = [
				discord.Embed(
					color=discord.Color(0x2f3136),
					description='\n'.join(page)
				).set_author(
					name=f'{ctx.author.name.title()}\'s Titles',
					icon_url=ctx.author.avatar_url_as(static_format='png')
				).set_footer(
					text=f'User ID: {ctx.author.id}'
				) for page in final
			]

			paginator = BotEmbedPaginator(ctx, embeds)
			await paginator.run()
		except:
			raise FailCommand('no titles achieved yet.')

	@is_registered()
	@_title.command(name='equip', help='Equips a title that you\'ve already achieved.')
	async def _equip(self, ctx, *, title):
		existingequipped = await self.check_equipped_title(ctx.author.id)

		if existingequipped:
			raise FailCommand('you already have a title equipped. can\'t have two titles at the same time, moron.')

		title = title.lower()
		existingtitle = await self.get_user_title(ctx.author.id, title)

		if not existingtitle:
			raise FailCommand('u don\'t have that title.. smh')

		getmulti = await self.multiplier(ctx.author)
		self.equipped.insert_one(
			{
				'uid':existingtitle['uid'],
				'title':existingtitle['title'],
				'icon':existingtitle['icon'],
				'bonus':existingtitle['bonus']
			}
		)

		equippedtitle = await self.get_equipped_title(ctx.author.id)
		addbonus = getmulti+equippedtitle['bonus']
		self.currency.update_one(
			{
				'uid':ctx.author.id
			},
			{
				'$set':{
					'multiplier':round(addbonus, 2)
				}
			}
		)

		await ctx.send(f'successfully equipped `{existingtitle["title"]}`.')

	@is_registered()
	@_title.command(name='unequip', help='Unequips the title equipped. No need to mention/input the title.')
	async def _unequip(self, ctx):
		equippedtitle = await self.get_equipped_title(ctx.author.id)

		if not equippedtitle:
			raise FailCommand('u don\'t have any title equipped, idiot.')

		getmulti = await self.multiplier(ctx.author)
		removebonus = getmulti-equippedtitle['bonus']
		self.currency.update_one(
			{
				'uid':ctx.author.id
			},
			{
				'$set':{
					'multiplier':round(removebonus, 2)
				}
			}
		)
		self.equipped.delete_one(
			{
				'uid':ctx.author.id
			}
		)

		await ctx.send(f'successfully unequipped the title `{equippedtitle["title"].title()}`.')


	@is_registered()
	@_title.command(name='dir', help='Shows all the titles that you can achieve.')
	async def _dir(self, ctx):
		achievements = self.achievements.find({})
		n = 5
		desc = []

		for x in achievements:
			desc.append(f'\U00002022 **{x["title"].title()}**\n**Description:** `{x["desc"]}`\n**Trigger CMD:** `{x["name"]}`\n')
		
		final = [desc[i*n:(i+1)*n] for i in range((len(desc)+n-1)//n)]
		embeds = [
			discord.Embed(
				title='**Title Dir**',
				description='\n'.join(page),
				color=discord.Color(0x2f3136)
			).set_thumbnail(
				url='https://cdn.discordapp.com/attachments/705399482422132740/728282293025898546/trash.gif'
			).set_footer(
				text=ctx.author,
				icon_url=ctx.author.avatar_url_as(static_format='png')
			) for page in final
		]

		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run()


	@is_registered()
	@commands.group(name='leaderboard', aliases=['lb', 'top'], help='Group command for leaderboards. Go check it out c;', invoke_without_command=True)
	async def _leaderboard(self, ctx):
		raise FailCommand('u need to invoke the subcommand for which leaderboard you want to see... smh\n*leaderboards available are: `cash`, `pet`, and `gamble`.*')

	@is_registered()
	@_leaderboard.command(name='cash', aliases=['richest'], help='Shows the money leaderboard, top richest players.')
	async def _cashlb(self, ctx):
		findall = self.currency.find({})
		user = await self.get_currency_info(ctx.author.id)

		n = 5
		op = []
		userbal = user['bal']
		users = []

		lst = [e for e in findall]
		lst.sort(key=lambda x: x['bal'], reverse=True)

		for i, ha in enumerate(lst):
			uid = ha['uid']
			bal = ha['bal']
			users.append(uid)
			emoji = '\U00002022 \U00002022 '
			if i+1 == 1:
				emoji = "\U0001f947"
			elif i+1 == 2:
				emoji = "\U0001f948"
			elif i+1 == 3:
				emoji = "\U0001f949"
			elif i+1 == len(lst):
				emoji = "\U0001f4a9"
			op.append(f'{emoji}`{i+1}` **{ha["uname"]}**\n\u200b \u00a0 \u00a0 `{bal}c`')

		uplace = users.index(ctx.author.id)
		final = [op[i*n:(i+1)*n] for i in range((len(op)+n-1)//n)]
		embs = [
			discord.Embed(
				title='Top Richest Players',
				color=discord.Color(0x2f3136),
				description='\n\n'.join(page)
			).add_field(
				name='ur place:',
				value=f'`{uplace+1}` {ctx.author} - **{userbal}c**'
			) for page in final
		]

		paginator = BotEmbedPaginator(ctx, embs)
		await paginator.run()

	@is_registered()
	@has_pet()
	@_leaderboard.command(name='pet', aliases=['strongest'], help='Shows the pet leaderboard, top strongest players.')
	async def _petlb(self, ctx):
		userpet = self.userpets.find_one(
			{
				'uid':ctx.author.id
			}
		)
		findall = self.userpets.find({})
		n = 5
		users = []
		op = []
		lst = [e for e in findall]
		lst.sort(key=lambda x: x['level'], reverse=True)

		for i,x in enumerate(lst):
			uname = self.currency.find_one(
				{
					'uid':x['uid']
				}
			)['uname']
			petname = await self.determine_nickname(x)
			icon = x['icon']
			level = x['level']
			users.append(x['uid'])
			op.append(f'{icon} `{i+1}` **{uname}** - Lv{level} {petname}')

		uplace = users.index(ctx.author.id)
		final = [op[i*n:(i+1)*n] for i in range((len(op)+n-1)//n)]
		pname = await self.determine_nickname(userpet)
		embeds = [
			discord.Embed(
				title='Top Strongest Pets',
				color=discord.Color(0x2f3136),
				description='\n'.join(page)
			).add_field(
				name='ur place:',
				value=f'{userpet["icon"]} `{uplace+1}` **{ctx.author}** - Lv{userpet["level"]} {pname}'
			) for page in final
		]

		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run()

	@commands.is_owner()
	@commands.command(name='bugreply', hidden=True)
	async def _bugreply(self, ctx, message:int, *, comments):
		await ctx.message.delete(delay=None)
		channel = self.bot.get_channel(734479371888492606)
		message = await channel.fetch_message(message)
		user = message.author
		valid = ['.png', '.gif', '.jpg', '.webp', '.jpeg']
		e = discord.Embed(color=discord.Color(0x2f3136), title=f"{user.name}'s Bug Report")
		try:
			attachment = message.attachments[0]
			for x in valid:
				if attachment.filename.lower().endswith(x):
					e.set_image(url=attachment.url)
					break
		except IndexError:
			pass
		e.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url_as(static_format='png'))
		e.description = f"{message.content}\n\n[Click here to jump to message.]({message.jump_url})"
		e.add_field(name="**Response:**", value=comments)
		await ctx.send(content=f"{user.mention}! {ctx.author.name} replied!",embed=e)

	@is_registered()
	@is_employed()
	@commands.group(invoke_without_command=True, name='job', help='Command used to see your job info. Also a parent command for job related commands. See subcommands for more info.')
	async def _job(self, ctx):
		userjob = await self.get_user_job(ctx.author.id)
		stats = await self.get_user_stats(ctx.author.id)
		company = await self.get_company_info(userjob['company'])
		e = discord.Embed(
			color=discord.Color(0x2f3136)
		)
		e.set_thumbnail(
			url=company['icon']
		)
		e.set_author(
			name=ctx.author,
			icon_url=ctx.author.avatar_url_as(static_format='png')
		)
		e.add_field(
			name="**\U00002022 Works for:**", 
			value=f"```css\n{userjob['company']}```"
		)
		e.add_field(
			name="**\U00002022 Position:**", 
			value=f"```css\n{userjob['job']}```"
		)
		e.add_field(
			name="\u200b", 
			value="\u200b"
		)
		e.add_field(
			name="**\U00002022 Pay range:**", 
			value=f"```css\n{userjob['pay1']}c - {userjob['pay2']}c```"
		)
		e.add_field(
			name="**\U00002022 Hours worked:**",
			value=f"```css\n{stats['workh']} hours```"
		)
		e.add_field(
			name="\u200b", 
			value="\u200b"
		)

		await ctx.send(embed=e)


	@is_registered()
	@is_unemployed()
	@_job.command(name='apply', help='Command used to apply for a job in a company.')
	async def _apply(self, ctx, cid):
		user = await self.get_currency_info(ctx.author.id)
		todaytime = await self.format_time(str(datetime.datetime.utcnow()))

		try:
			lastapplied = user['lastapplied']
		except KeyError:
			lastapplied = await self.format_time("2020-07-23 21:21:23.170014")

		formula = todaytime - lastapplied
		rmtime = datetime.timedelta(hours=24, minutes=0) - formula

		if formula.days <= 0:
			ts = rmtime.total_seconds()
			h, m = ts//3600, (ts%3600)//60

			if h == 0:
				raise FailCommand(f'smfh, wait after `{int(m)}m`  before applying for another work again. impatient much?')
			else:
				raise FailCommand(f'smfh, wait after `{int(h)}h` and `{int(m)}m` before applying for another work again. impatient much?')

		job = await self.get_job_info(cid.lower())

		if not job:
			raise FailCommand('can\'t find the job that you\'re applying for. check again.')

		fjob = await self.get_precise_job_info(job['name'], job['positions'][0])

		if not fjob:
			lu = await self.bot.get_user(342361263768207360)
			await lu.send('line 3007 in economy.py raised an error. `fjob` could not be found.')

		self.userjobs.insert_one(
			{
				'uid':ctx.author.id,
				'company':fjob['job'],
				'pay1':fjob['range1'],
				'pay2':fjob['range2']
			}
		)

		await ctx.send(f"success. you're now working for {fjob['company']}. your current position is `{fjob['job']}`. do `{ctx.prefix}job` to see your work information.")

	@is_registered()
	@_job.command(name='list', help='Shows a list of available jobs in a company.')
	async def __list(self, ctx):
		jobs = self.jobs.find({})
		op = []
		n = 5

		for x in jobs:
			kek = f"**Company ID:** `{x['cid']}`\n**Company:** {x['name']}\n**Owner:** {x['owner']}\n**Total Work Hour required:** `{x['req']}`\n**Positions:**\n"

			for z in x['positions']:
				findjob = self.job.find_one({"job":z})

				if z == "Drive-Thru Operator":
					kek += f"`- {z}`\n"
				else:
					kek += f"`- {z} (Promoted after {findjob['req']} work hours.)`\n"

			op.append(kek)

		final = [op[i*n:(i+1)*n] for i in range((len(op)+n-1)//n)]
		embeds = [
			discord.Embed(
				title="Available Jobs",
				description="\n".join(page),
				color=discord.Color(0x2f3136)
			).add_field(
				name="**════════════════════════════════**",
				value=f"To apply: `{ctx.prefix}job apply <companyid>`"
			).set_footer(
				text=ctx.author,
				icon_url=ctx.author.avatar_url_as(static_format='png')
			) for page in final
		]

		paginator = BotEmbedPaginator(ctx, embeds)
		await paginator.run()

	@is_registered()
	@is_employed()
	@commands.command(name='work', help='Command used to work, can be used every 1h. Get promoted after a certain amount of work hours.')
	async def _work(self, ctx):
		user = await self.get_currency_info(ctx.author.id)
		job = await self.get_user_job(ctx.author.id)

		try:
			lastwork = user['lastwork']
		except KeyError:
			lastwork = await self.format_time("2020-07-20 21:21:23.170014")

		todayd = await self.format_time(str(datetime.datetime.utcnow()))
		formula = todayd - lastwork
		rmtime = datetime.timedelta(hours=1, minutes=0) - formula
		ts = rmtime.total_seconds()
		h, m, s = ts//3600, (ts%3600)//60, ts%60

		if h == 0:
			if m <= 0:
				find = await self.get_precise_job_info(job['company'], job['job'])
				stats = await self.get_user_stats(ctx.author.id)
				workh = stats['workh']
				amount = random.randint(job['pay1'], job['pay2'])
				pay, resp = await self.work_rng(amount)

				if job['job'] == 'CEO':
					pay = amount
					resp = ''

				response = random.choice(find['resp'])
				lfnewb = await self.get_balance(ctx.author.id)

				self.currency.update_one(
					{
						'uid':ctx.author.id
					},
					{
						'$set':{
							'bal':int(lfnewb+pay)
						}
					}
				)
				self.usercmd.update_one(
					{
						'uid':ctx.author.id
					},
					{
						'$set':{
							'workh':int(workh+1)
						}
					}
				)
				self.currency.update_one(
					{
						'uid':ctx.author.id
					},
					{
						'$set':{
							'lastwork':todayd
						}
					}
				)
				company = await self.get_company_info(job['company'])
				self.jobs.update_one(
					{
						'name':job['company']
					},
					{
						'$set':{
							'netw':int(company['netw']+10)
						}
					}
				)
				await self.addTotalBal(ctx, pay)
				await self.addTotalWorkH(ctx)
				await self.companyIncome(ctx, 10)
				await self.addLogToCompany(ctx, str(job['company']), 10, pay)
				await self.promote(ctx)

				await ctx.send(f"{response}\n{resp}\n`Earned: {pay}c`")

			else:
				raise FailCommand(f"try again after `{int(m)}m` before working again.. smh")
		else:
			find = await self.get_precise_job_info(job['company'], job['job'])
			stats = await self.get_user_stats(ctx.author.id)
			workh = stats['workh']
			amount = random.randint(job['pay1'], job['pay2'])
			pay, resp = await self.work_rng(amount)

			if job['job'] == 'CEO':
				pay = amount
				resp = ''

			response = random.choice(find['resp'])
			lfnewb = await self.get_balance(ctx.author.id)

			self.currency.update_one(
				{
					'uid':ctx.author.id
				},
				{
					'$set':{
						'bal':int(lfnewb+pay)
					}
				}
			)
			self.usercmd.update_one(
				{
					'uid':ctx.author.id
				},
				{
					'$set':{
						'workh':int(workh+1)
					}
				}
			)
			self.currency.update_one(
				{
					'uid':ctx.author.id
				},
				{
					'$set':{
						'lastwork':todayd
					}
				}
			)
			company = await self.get_company_info(job['company'])
			self.jobs.update_one(
				{
					'name':job['company']
				},
				{
					'$set':{
						'netw':int(company['netw']+10)
					}
				}
			)
			await self.addTotalBal(ctx, pay)
			await self.addTotalWorkH(ctx)
			await self.companyIncome(ctx, 10)
			await self.addLogToCompany(ctx, str(job['company']), 10, pay)
			await self.promote(ctx)
			await ctx.send(f"{response}\n{resp}\n`Earned: {pay}c`")

	@is_registered()
	@is_CEO()
	@commands.group(invoke_without_command=True, name='company', help='Shows your company information if you\'re a company owner. Also a parent command for company-related commands. See subcommands for more info.')
	async def _company(self, ctx):
		c_owner = await self.get_company_owner(ctx.author.id)
		find = self.userjobs.find({})
		n = len([e['company'] == c_owner['name'] for e in find])
		worth = c_owner['netw'] - (c_owner['netw']*0.2)

		e = discord.Embed(
			color=discord.Color(0x2f3136)
		)
		e.set_author(
			name=f"{ctx.author}'s Company", 
			icon_url=ctx.author.avatar_url_as(static_format='png')
		)
		e.set_thumbnail(
			url=f"{c_owner['icon']}"
		)
		e.add_field(
			name="**\U00002022 Company Name:**", 
			value=f"```css\n{c_owner['name']}```", 
			inline=False
		)
		e.add_field(
			name="**\U00002022 Net Worth:**", 
			value=f"```css\n{int(worth)}c```"
		)
		e.add_field(
			name="**\U00002022 # of Employees:**", 
			value=f"```css\n{n}```"
		)
		e.add_field(
			name="\u200b", 
			value="\u200b"
		)
		e.add_field(
			name="**\U00002022 Company Bal:**", 
			value=f"```css\n{c_owner['bal']}c```"
		)
		e.add_field(
			name="**\U00002022 Date Created:**", 
			value=f"```css\n{humanize.naturaldate(c_owner['created_at'])}```"
			)
		e.add_field(
			name="\u200b", 
			value="\u200b"
		)

		await ctx.send(embed=e)


	@is_registered()
	@is_CEO()
	@_company.command(name='withdraw', help='Command used to withdraw your company\'s bal.')
	async def _withdraw(self, ctx, amount:convert_this):
		c_owner = await self.get_company_owner(ctx.author.id)

		if amount in ['all', 'max']:
			amount = c_owner['bal']

		if c_owner['bal'] == 0:
			raise FailCommand('your company already don\'t have anything in it, smh.')

		if amount <= 0:
			raise NiceTry('lmao nice try.')

		self.jobs.update_one(
			{
				'owner_id':ctx.author.id
			},
			{
				'$set':{
					'bal':int(c_owner['bal']-amount)
				}
			}
		)

		owner_bal = await self.get_balance(c_owner['owner_id'])
		self.currency.update_one(
			{
				'uid':c_owner['owner_id']
			},
			{
				'$set':{
					'bal':int(owner_bal+amount)
				}
			}
		)

		await self.addLogToCompany(ctx, str(c_owner['name']), amount, 0)
		await ctx.send(f"successfully withdrew `{amount}c` from the company.")

	@is_registered()
	@is_CEO()
	@_company.command(name='deposit', help='Command used to deposit to your company\'s bal.')
	async def _deposit(self, ctx, amount:convert_this):
		company = await self.get_company_owner(ctx.author.id)
		uinf = await self.get_currency_info(ctx.author.id)

		if uinf['bal'] <= 0:
			raise FailCommand('what are you exactly trying to deposit?? u don\'t have anything. smh')

		if amount in ['all', 'max']:
			amount = uinf['bal']

		if amount <= 0:
			raise NiceTry('lmao what? nice try stupid but no.')

		self.jobs.update_one(
			{
				'owner_id':ctx.author.id
			},
			{
				'$set':{
					'bal':int(company['bal']+amount)
				}
			}
		)

		owner_bal = await self.get_balance(company['owner_id'])
		self.currency.update_one(
			{
				'uid':company['owner_id']
			},
			{
				'$set':{
					'bal':int(owner_bal-amount)
				}
			}
		)

		await self.addLogToCompany(ctx, str(company['name']), amount, 0)
		await ctx.send(f"successfully deposited `{amount}c` to the company.")


		

	@is_registered()
	@is_CEO()
	@_company.command(name='logs', help='Command used to see your company\'s logs. You can also add `clear` to clear your company\'s logs.')
	async def _logs(self, ctx, action:str=None):
		if action is None:
			c_owner = await self.get_company_owner(ctx.author.id)

			if len(c_owner['logs']) == 0:
				return await ctx.send('empty.')

			logs = c_owner['logs'][::-1]
			op = []
			n = 5

			for z in logs:
				op.append(f"`\U00002022 {z}`")

			final = [op[i*n:(i+1)*n] for i in range((len(op)+n-1)//n)]
			embeds = [
				discord.Embed(
					description="\n".join(page),
					color=discord.Color(0x2f3136)
				).set_thumbnail(
					url=f"{c_owner['icon']}"
				).set_author(
				name=f"{ctx.author}'s Company Logs", 
				icon_url=ctx.author.avatar_url_as(static_format='png')
				) for page in final
			]
			
			paginator = BotEmbedPaginator(ctx, embeds)
			await paginator.run()
		elif action.lower() == 'clear':
			self.jobs.update_one(
				{
					"owner_id":ctx.author.id
				}, 
				{
					"$set":{
						"logs":[]
					}
				}
			)

			await ctx.send('successfully cleared logs for your company.')

	@is_registered()
	@is_employed()
	@commands.command(name='resign', help='Commands used when you want to end your career and look for a new one.')
	async def _resign(self, ctx):
		self.userjobs.delete_one(
			{
				'uid':ctx.author.id
			}
		)
		self.usercmd.update_one(
			{
				'uid':ctx.author.id
			},
			{
				'$set':{
					'workh':0
				}
			}
		)
		hehe = await self.format_time(str(datetime.datetime.utcnow()))
		self.currency.update_one(
			{
				"uid":ctx.author.id
			}, 
			{
				"$set":{
					"lastapplied":hehe
				}
			}
		)
		await ctx.send(f"successfully left **{hasjob['company']}**. now u have to wait for a day to get another job again.")

	@is_registered()
	@commands.command(name='vote', help='Command used to vote the bot and get rewards!')
	async def _vote(self, ctx):
		votes = await self.get_user_votes(ctx.author.id)
		heh = await self.next_vote(ctx.author.id)
		e = discord.Embed(
			color=discord.Color(0x2f3136),
			description=f'vote [here](http://trashbot.lulu.cf/vote) or [here](https://top.gg/bot/733645780925284413/vote) if that one doesn\'t work.\n\n*remember to vote again after 12h* c;\n\n'
		)
		e.set_author(
			name='Vote for trashbot in top.gg',
			icon_url='https://top.gg/images/logotrans.png'
		)
		e.set_thumbnail(
			url='https://cdn.discordapp.com/attachments/736200150837493822/756243094273523804/vote_me.png'
		)
		e.add_field(
			name=f'**Your Votes: {votes}**',
			value=heh
		)

		await ctx.send(embed=e)

	@commands.command(name='emoji')
	async def _emoji(self, ctx, emoji):

		def emoji_convert(emoji):
			"""Manual Conversion of Discord Emojis"""
			emoji = emoji.replace('<', '').replace('>', '').split(':')
			base_url = 'https://cdn.discordapp.com/emojis/'

			if emoji[0] == 'a':
				return f'{base_url}{emoji[2]}.gif?v=1', emoji[1]
			return f'{base_url}{emoji[2]}.png?v=1', emoji[1]

		emoji_url, emoji_name = emoji_convert(emoji)

		await ctx.send(f'`Name:` {emoji_name}\n`URL:` {emoji_url}')


	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		error = getattr(error, 'original', error)

		if hasattr(ctx.command, 'on_error'):
			return

		elif isinstance(error, commands.CommandNotFound):
			return

		elif isinstance(error, commands.MissingRequiredArgument):
			if ctx.command.name == 'rep':
				return await ctx.send('maybe let me know who u wanna rep.')
			return await ctx.send(content=f'u missed an argument: `{error.param.name}`.')

		elif isinstance(error, commands.CommandOnCooldown):
			c = humanize.naturaldelta(datetime.timedelta(seconds=error.retry_after))
			return await ctx.send(content=f'calm down, try again after `{c}`. sooo fucking impatient smh.', delete_after=error.retry_after)

		await ctx.send(content=error)


def setup(bot):
	bot.add_cog(Economy(bot))