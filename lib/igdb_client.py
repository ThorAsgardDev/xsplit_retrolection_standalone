
import sys
import traceback
import datetime
import requests
import urllib.parse


class IgdbClient:
	# The list of platforms can be retrieved using:
	# https://api-v3.igdb.com/platforms
	# fields *; limit 200;
	RETROLECTION_PLATFORM_LABEL_TO_ID = {
		"Dreamcast": "23",
		"GameBoy": "33",
		"GameBoyAdvance": "24",
		"GameBoyColor": "22",
		"GameCube": "21",
		"GameGear": "35",
		"MasterSystem": "64",
		"Megadrive": "29, 30, 78",
		"Nes": "18, 99",
		"Nintendo64": "4",
		"PC GOG": "6, 13",
		"PC Windows": "6, 13",
		"Playstation": "7",
		"Playstation2": "8",
		"Saturn": "32",
		"SuperNes": "19, 58",
		"Xbox": "11",
	}
	
	def __init__(self, api_key):
		self.api_key = api_key
		
	def send_request(self, path, data):
		try:
			headers = {
				"Accept": "application/json",
				"user-key": "b8510016e1efe34981973d3f6a4f8e22",
			}
			url = "https://api-v3.igdb.com" + path
			response = requests.post(url, headers = headers, data = data)
			if response.status_code != 200:
				print("BAD STATUS: " + str(response))
				return
			return response.json()
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			return
			
	def search_game_by_name(self, name, retrolection_platform_label):
		name = name.strip()
		games = []
		finished = False
		while finished == False:
			data = 'fields game, name; where game.platforms = (' + \
				IgdbClient.RETROLECTION_PLATFORM_LABEL_TO_ID[retrolection_platform_label] + \
				') & (name ~ *"' + name + '"* | alternative_name ~ *"' + name + '"*); limit 50;'
			response = self.send_request("/search", data)
			if len(response) >= 1 or len(name) < 4:
				finished = True
			else:
				if len(name) >= 11:
					name = name[:10]
				else:
					name = name[:-1]
					
		for found_game in response:
			game = {
				"id": found_game["game"],
				"title": found_game["name"],
			}
			games.append(game)
			
		return games
		
	def get_game_info(self, id):
		info = {}
		data = 'fields name, alternative_names.name, game_modes.name, cover.image_id, first_release_date, involved_companies.company.name; where id = ' + str(id) + ';'
		response = self.send_request("/games", data)
		if not response:
			return
		game = response[0]
		info["title"] = ""
		if ("name" in game) and game["name"]:
			info["title"] = game["name"]
		info["release_date"] = ""
		if ("first_release_date" in game) and game["first_release_date"]:
			info["release_date"] = datetime.datetime.utcfromtimestamp(game["first_release_date"]).strftime("%Y-%b-%d")
			
		modes = ""
		if ("game_modes" in game) and game["game_modes"]:
			for v in game["game_modes"]:
				if v["name"]:
					if modes != "":
						modes += ", "
					modes += v["name"]
		info["modes"] = modes
		
		alternates = ""
		if ("alternative_names" in game) and game["alternative_names"]:
			for v in game["alternative_names"]:
				if v["name"]:
					if alternates != "":
						alternates += ", "
					alternates += v["name"].replace("\n", " ")
		info["alternates"] = alternates
		
		info["url_image"] = None
		if ("cover" in game) and game["cover"] and game["cover"]["image_id"]:
			info["url_image"] = "https://images.igdb.com/igdb/image/upload/t_1080p/" + game["cover"]["image_id"] + ".jpg"
			
		return info
		