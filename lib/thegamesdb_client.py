
import sys
import traceback
import datetime
import requests
import urllib.parse
import time


class TheGamesDbClient:
	# TheGamesDB plaforms id are indicated in the url of the web site
	RETROLECTION_PLATFORM_LABEL_TO_THEGAMESDB_ID = {
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
	
	def __init__(self, api_key):
		self.api_key = api_key
		
	def send_request(self, path, param = None):
		try:
			if not param:
				param = {}
			param["apikey"] = self.api_key
			url = "https://api.thegamesdb.net/v1" + path + "?" + urllib.parse.urlencode(param, True)
			response = requests.get(url)
			if response.status_code != 200:
				print("BAD STATUS: ", response)
				return
			return response.json()
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			return
			
	def search_game_by_name(self, name, retrolection_platform_label):
		st = time.time()
		games = []
		param = {
			"name": name,
			"filter[platform][]": TheGamesDbClient.RETROLECTION_PLATFORM_LABEL_TO_THEGAMESDB_ID[retrolection_platform_label],
		}
		response = self.send_request("/Games/ByGameName", param)
		print(time.time(), "search_game_by_name (ms): ", (time.time() - st) * 1000)
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
		st = time.time()
		info = {}
		param = {
			"id": id,
			"fields": "players,genres,coop,alternates",
			"include": "boxart",
		}
		response = self.send_request("/Games/ByGameID", param)
		print(time.time(), "get_game_info (ms): ", (time.time() - st) * 1000)
		if not response:
			return
			
		game = response["data"]["games"][0]
		info["title"] = ""
		if game["game_title"]:
			info["title"] = game["game_title"]
		info["release_date"] = ""
		if game["release_date"]:
			info["release_date"] = datetime.datetime.strptime(game["release_date"], '%Y-%m-%d').strftime("%Y-%b-%d")
			
		modes = ""
		if game["players"]:
			modes += str(game["players"]) + " joueur(s)"
		if game["coop"]:
			if modes != "":
				modes += ", "
			modes += "coop: " + game["coop"]
		info["modes"] = modes
		
		alternates = ""
		if game["alternates"]:
			for v in game["alternates"]:
				if alternates != "":
					alternates += ", "
				alternates += v
		info["alternates"] = alternates
		
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
				info["url_image_thumb"] = boxart_base_url["thumb"] + filename
				info["url_image"] = boxart_base_url["original"] + filename
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			
		return info
		