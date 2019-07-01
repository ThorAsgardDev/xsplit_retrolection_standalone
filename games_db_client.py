
import sys
import traceback
import datetime
import requests
import urllib.parse


MONTH_TO_STR = [
	"Janvier",
	"Février",
	"Mars",
	"Avril",
	"Mai",
	"Juin",
	"Juillet",
	"Août",
	"Septembre",
	"Octobre",
	"Novembre",
	"Décembre",
]

class GamesDbClient:
	# TheGamesDB plaforms id are indicated in the url of the web site
	RETROLECTION_PLATFORM_LABEL_TO_THE_GAMES_DB_ID = {
		"Dreamcast": [16],
		"GameBoy": [4],
		"GameBoyAdvance": [5],
		"GameBoyColor": [41],
		"GameCube": [2],
		"GameGear": [20],
		"MasterSystem": [35],
		"Megadrive": [18, 36],
		"Nes": [7],
		"Nintendo64": [3],
		"PC GOG": [1],
		"PC Windows": [1],
		"Playstation": [10],
		"Playstation2": [11],
		"Saturn": [17],
		"SuperNes": [6],
		"Xbox": [14],
	}
	
	# IGDB Get platforms id (use list_igdb_platforms method from this class)
	RETROLECTION_PLATFORM_LABEL_TO_IGDB_ID = {
		"Dreamcast": [23],
		"GameBoy": [33],
		"GameBoyAdvance": [24],
		"GameBoyColor": [22],
		"GameCube": [21],
		"GameGear": [35],
		"MasterSystem": [64],
		"Megadrive": [29],
		"Nes": [18],
		"Nintendo64": [4],
		"PC GOG": [6],
		"PC Windows": [6],
		"Playstation": [7],
		"Playstation2": [8],
		"Saturn": [32],
		"SuperNes": [19],
		"Xbox": [11],
	}
	
	def __init__(self, the_games_db_api_key, igdb_api_key):
		self.the_games_db_api_key = the_games_db_api_key
		self.igdb_api_key = igdb_api_key
		self.the_game_db_developers = self.list_the_game_db_developers()
		self.the_game_db_publishers = self.list_the_game_db_publishers()
		
	def send_the_games_db_request(self, path, param = None):
		if not param:
			param = {}
		param["apikey"] = self.the_games_db_api_key
		url = "https://api.thegamesdb.net" + path + "?" + urllib.parse.urlencode(param, True)
		response = requests.get(url)
		if response.status_code != 200:
			print("BAD STATUS: " + response)
			return
		return response.json()
		
	def send_igdb_request(self, path, data):
		headers = {
			"user-key": self.igdb_api_key,
			"Accept": "application/json",
		}
		url = "https://api-v3.igdb.com" + path
		response = requests.post(url, headers = headers, data = data)
		if response.status_code != 200:
			print("BAD STATUS: " + response)
			return
		return response.json()
		
	def list_igdb_platforms(self):
		for i in range(5):
			data = "fields name; limit 50; offset " + str(i * 50) + ";"
			print(self.send_igdb_request("/platforms", data))
			
	def list_the_game_db_developers(self):
		response = self.send_the_games_db_request("/Developers")
		if not response:
			return
		return response["data"]["developers"]
		
	def list_the_game_db_publishers(self):
		response = self.send_the_games_db_request("/Publishers")
		if not response:
			return
		return response["data"]["publishers"]
		
	def search_game_by_name(self, name, retrolection_platform_label):
		games = []
		param = {
			"name": name,
			"filter[platform][]": GamesDbClient.RETROLECTION_PLATFORM_LABEL_TO_THE_GAMES_DB_ID[retrolection_platform_label],
		}
		response = self.send_the_games_db_request("/Games/ByGameName", param)
		if not response:
			return
		found_games = response["data"]["games"]
		for found_game in found_games:
			game = {
				"id": found_game["id"],
				"title": found_game["game_title"],
			}
			games.append(game)
			
		return games
		
	def get_game_info(self, id):
		info = {}
		param = {
			"id": id,
			"fields": "players,publishers,genres,coop,alternates",
			"include": "boxart",
		}
		response = self.send_the_games_db_request("/Games/ByGameID", param)
		if not response:
			return
			
		game = response["data"]["games"][0]
		info["title"] = ""
		if game["game_title"]:
			info["title"] = game["game_title"]
		info["release_date"] = ""
		if game["release_date"]:
			info["release_date"] = datetime.datetime.strptime(game["release_date"], '%Y-%m-%d').strftime("%Y-%b-%d")
		info["players"] = ""
		if game["players"]:
			info["players"] = game["players"]
		info["coop"] = ""
		if game["coop"]:
			info["coop"] = game["coop"]
		alternates = ""
		if game["alternates"]:
			for v in game["alternates"]:
				if alternates != "":
					alternates += ", "
				alternates += v
		info["alternates"] = alternates
		
		info["developers"] = ""
		info["publishers"] = ""
		
		try:
			developers = ""
			if game["developers"]:
				for v in game["developers"]:
					if developers != "":
						developers += ", "
				developers += self.the_game_db_developers[str(v)]["name"]
			info["developers"] = developers
			
			publishers = ""
			if game["publishers"]:
				for v in game["publishers"]:
					if publishers != "":
						publishers += ", "
				publishers += self.the_game_db_publishers[str(v)]["name"]
			info["publishers"] = publishers
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			
		try:
			boxart = response["include"]["boxart"]
			boxart_data = boxart["data"][str(id)]
			filename = None
			for v in boxart_data:
				if v["type"] == "boxart" and v["side"] == "front":
					filename = v["filename"]
					break
			if filename:
				boxart_base_url = boxart["base_url"]
				info["url_image"] = boxart_base_url["original"] + filename
				info["url_image_thumbnail"] = boxart_base_url["thumb"] + filename
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			
		return info
			
	def get_platform_info(self, retrolection_platform_label):
		info = {}
		
		id = GamesDbClient.RETROLECTION_PLATFORM_LABEL_TO_THE_GAMES_DB_ID[retrolection_platform_label][0]
		param = {
			"id": id,
			"fields": "manufacturer,media,cpu,memory,graphics,sound,maxcontrollers,display,youtube",
		}
		response = self.send_the_games_db_request("/Platforms/ByPlatformID", param)
		if not response:
			return
		platform = response["data"]["platforms"][str(id)]
		
		info["name"] = ""
		info["manufacturer"] = ""
		info["media"] = ""
		info["cpu"] = ""
		info["memory"] = ""
		info["graphics"] = ""
		info["sound"] = ""
		info["max_controllers"] = ""
		info["display"] = ""
		info["release_date_japan"] = ""
		info["release_date_us"] = ""
		info["release_date_eu"] = ""
		
		if platform["name"]:
			info["name"] = platform["name"]
		if platform["manufacturer"]:
			info["manufacturer"] = platform["manufacturer"]
		if platform["media"]:
			info["media"] = platform["media"]
		if platform["cpu"]:
			info["cpu"] = platform["cpu"]
		if platform["memory"]:
			info["memory"] = platform["memory"]
		if platform["graphics"]:
			info["graphics"] = platform["graphics"]
		if platform["sound"]:
			info["sound"] = platform["sound"]
		if platform["maxcontrollers"]:
			info["max_controllers"] = platform["maxcontrollers"]
		if platform["display"]:
			info["display"] = platform["display"]
			
		data = "fields versions.platform_version_release_dates.*; where id = " + str(GamesDbClient.RETROLECTION_PLATFORM_LABEL_TO_IGDB_ID[retrolection_platform_label][0]) + "; sort versions.platform_version_release_dates.date;"
		response = self.send_igdb_request("/platforms", data)
		if not response:
			return
		platform_version_release_dates = response[0]["versions"][0]["platform_version_release_dates"]
		for platform_version_release_date in platform_version_release_dates:
			if "region" in platform_version_release_date:
				region = platform_version_release_date["region"]
				date = platform_version_release_date["human"]
				if region == 1: # Europe
					info["release_date_eu"] = date
				elif region == 2: # US
					info["release_date_us"] = date
				elif region == 5: # Japan
					info["release_date_japan"] = date
				
		return info
