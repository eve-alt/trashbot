import math
import random
import secrets as secs
import pymongo
import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient

class PetData(object):
	cluster = MongoClient("mongodb+srv://user:pass@daycare-assistant-3nvb4.mongodb.net/daycare-assistant?retryWrites=true&w=majority")
	db = cluster["discord"]
	userpets = db["userpets"]
	def __init__(self, owner_id):
		self.userpets = PetData.userpets.find_one({"uid":owner_id})

		self.p_level = self.userpets['level']
		self.pet_icon = self.userpets['icon']
		self.p_equips = self.userpets['equipments']
		self.p_hp = self.userpets['hp']

		self.p_str = self.userpets['str']
		self.p_agi = self.userpets['agi']
		self.p_int = self.userpets['int']
		self.p_vit = self.userpets['vit']
		self.p_dex = self.userpets['dex']
		self.p_luk = self.userpets['luk']

		self.p_weapon = self.p_equips['weapon']
		self.p_armor = self.p_equips['armor']
		self.p_boots = self.p_equips['boots']
		self.p_helm = self.p_equips['helm']
		self.p_mask = self.p_equips['mask']
		self.p_mouth = self.p_equips['mouth']
		self.p_robe = self.p_equips['robe']
		self.p_accessoryL = self.p_equips['accessory_left']
		self.p_accessoryR = self.p_equips['accessory_right']

		self.w_variance = (0.05 * self.p_weapon['rarity'] * self.p_weapon['pdmg'])*((secs.randbelow(2)*2) - 1)
		self.w_statBonus = self.p_weapon['pdmg']*self.p_str/200
		self.w_refinementBonus = self.p_weapon['refine']*self.p_weapon['rarity']
		self.atk_statusATK = int((self.p_level/4)+self.p_str+(self.p_dex/5)+(self.p_luk/3))
		self.atk_weaponATK = int(self.p_weapon['pdmg']+self.w_variance+self.w_statBonus+self.w_refinementBonus)
		
		self.mw_variance = (0.1 * self.p_weapon['rarity'] * (self.p_weapon['mdmg'] + (self.p_weapon['refine'] * 2.5)))*((secs.randbelow(2)*2) - 1)
		self.mw_refinementBonus = self.p_weapon['refine']*self.p_weapon['rarity']
		self.matk_statusMATK = int((self.p_level/4) + self.p_int + (self.p_int//2) + (self.p_dex//5) + (self.p_luk//3))
		self.matk_weaponMATK = int(self.p_weapon['mdmg']+self.mw_variance+self.mw_refinementBonus)

		self.pdef_hardDEF = int(self.p_armor['pdef']+self.p_boots['pdef']+self.p_helm['pdef']+self.p_mask['pdef']+self.p_mouth['pdef']+self.p_robe['pdef'])
		self.pdef_softDEF = int((self.p_vit/2) + (self.p_agi/5) + (self.p_level/2))

		self.mdef_hardDEF = int(self.p_armor['mdef']+self.p_boots['mdef']+self.p_helm['mdef']+self.p_mask['mdef']+self.p_mouth['mdef']+self.p_robe['mdef'])
		self.mdef_softDEF = int(self.p_int+(self.p_vit/5)+(self.p_dex/5)+(self.p_level/4))


	@property
	def atk(self):
		return int(self.atk_statusATK+self.atk_weaponATK)

	@property
	def matk(self):
		return int(self.matk_weaponMATK+self.matk_statusMATK)

	@property
	def pdef(self):
		return int(self.pdef_softDEF + self.pdef_hardDEF)

	@property
	def mdef(self):
		return int(self.mdef_softDEF + self.mdef_hardDEF)

	@property
	def hit(self):
		return int(175+self.p_level+self.p_dex+(self.p_luk/3))

	@property
	def flee(self):
		return int(100+(self.p_level+self.p_agi+self.p_luk/5))

	@property
	def icon(self):
		return str(self.pet_icon)

	@property
	def nickname(self):
		if self.userpets['petnick'] == "none":
			return self.userpets['petname']
		else:
			return self.userpets['petnick']
	
	
	
class Pet(object):
	output = ""
	field = ""
	def __init__(self, name, owner_id):
		self.name = name
		self.owner_id = owner_id
		self.data = PetData(self.owner_id)
		self.still_health = int(self.data.p_hp)
		self.health = int(self.data.p_hp)

	@property
	def alive(self):
		return self.health > 0

	def getBar(self, percent):
		if percent <= 9:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 10 and percent <= 19:
			pek = "<:sf:730308838364020757><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 20 and percent <= 29:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 30 and percent <= 39:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 40 and percent <= 49:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 50 and percent <= 59:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 60 and percent <= 69:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 70 and percent <= 79:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 80 and percent <= 89:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 90 and percent <= 99:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ee:730310211285286935>"
			return pek
		else:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek

	def getBarp2(self, percent):
		if percent <= 9:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ee:730310211285286935>"
			return pek
		elif percent >= 10 and percent <=19:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:ef:730310208773160980>"
			return pek
		elif percent >= 20 and percent <= 29:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		elif percent >= 30 and percent <= 39:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		elif percent >= 40 and percent <= 49:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		elif percent >= 50 and percent <= 59:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		elif percent >= 60 and percent <= 69:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:me:730308837688606750><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		elif percent >= 70 and percent <= 79:
			pek = "<:se:730308837915230327><:me:730308837688606750><:me:730308837688606750><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		elif percent >= 80 and percent <= 89:
			pek = "<:se:730308837915230327><:me:730308837688606750><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		elif percent >= 90 and percent <= 99:
			pek = "<:se:730308837915230327><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek
		else:
			pek = "<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>"
			return pek

	def getPercent(self, n1:float, n2:float):
		return int(n1/n2*100)

	def take_turn(self, other, x, turn1):
		dodge_rate = self.data.hit - other.data.flee
		n = random.randint(1, 100)
		if n < dodge_rate:
			damage = int((self.data.atk*(4000 + other.data.pdef_hardDEF) / (4000 + other.data.pdef_hardDEF * 10))-other.data.pdef_softDEF)
			if damage < 0:
				damage = 0
			other.health = math.floor(max(other.health - damage, 0))
			Pet.output = f"**Turn {x}:**\n`{self.name} {self.data.hit} - {other.name} {other.data.flee} = {dodge_rate}`\n{self.name}'s {self.data.icon} {self.data.nickname} is attacking {other.name}'s {other.data.icon} {other.data.nickname}.\n\n{self.data.icon}{self.data.nickname} attacked {other.data.icon}{other.data.nickname} for {damage}dmg.\n"
			pbar = ""
			if turn1:
				prcnt = self.getPercent(other.health, other.still_health)
				pbar = self.getBar(prcnt)
				Pet.field = f"{other.health}/{other.still_health}\n{pbar}"
			else:
				prcnt = self.getPercent(other.health, other.still_health)
				pbar = self.getBarp2(prcnt)
				Pet.field = f"{other.health}/{other.still_health}\n{pbar}"
		else:
			Pet.output = f"**Turn {x}:**\n`{self.name} {self.data.hit} - {other.name} {other.data.flee} = {dodge_rate}`\n{self.name} tried to attack {other.name} and missed.\n"
			pbar = ""
			if turn1:
				prcnt = self.getPercent(other.health, other.still_health)
				pbar = self.getBar(prcnt)
				Pet.field = f"{other.health}/{other.still_health}\n{pbar}"
			else:
				prcnt = self.getPercent(other.health, other.still_health)
				pbar = self.getBarp2(prcnt)
				Pet.field = f"{other.health}/{other.still_health}\n{pbar}"

	@staticmethod
	async def duel(channel:discord.TextChannel, p1, p2):
		turn1 = True
		e = discord.Embed(color=discord.Color(0x2f3136))
		e.title = f"Duel between {p1.name} and {p2.name}!"
		e.add_field(name=f"{p2.name}'s {p2.data.icon} HP Bar", value=f"{p2.health}/{p2.still_health}\n<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>")
		e.add_field(name=f"{p1.name}'s {p1.data.icon} HP Bar", value=f"{p1.health}/{p1.still_health}\n<:sf:730308838364020757><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:mf:730308836812128276><:ef:730310208773160980>")
		m1 = await channel.send(embed=e)
		await asyncio.sleep(2)
		x = 0
		while p1.alive and p2.alive:
			x += 1
			if turn1:
				p1.take_turn(p2, x, turn1)
				turn1 = False
				e.description = Pet.output
				e.set_field_at(0, name=f"{p2.name}'s {p2.data.icon} HP Bar", value=Pet.field)
				await m1.edit(embed=e)
				await asyncio.sleep(2)
			else:
				p2.take_turn(p1, x, turn1)
				turn1 = True
				e.description = Pet.output
				e.set_field_at(1, name=f"{p1.name}'s {p1.data.icon} HP Bar", value=Pet.field)
				await m1.edit(embed=e)
				await asyncio.sleep(2)

		if p1.alive:
			Pet.output = f"{p1.name}'s {p1.data.nickname} won."
			e.description = Pet.output
			await m1.edit(embed=e)
		else:
			Pet.output = f"{p2.name}'s {p2.data.nickname} won."
			e.description = Pet.output
			await m1.edit(embed=e)