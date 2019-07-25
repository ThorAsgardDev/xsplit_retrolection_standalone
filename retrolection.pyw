
import os
import traceback
import configparser
import requests
import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk
import lib.sheets_client
import lib.games_db_client
import lib.utils
import lib.canvas_cover


class MainFrame(tkinter.Frame):
	TOKENS_FILENAME = "tokens.ini"
	RESIZED_COVER_FILE_NAME = "cover.png"
	SCRAPER_COVER_FILE_NAME = "scraper_cover.png"
	
	def __init__(self, window, **kwargs):
		tkinter.Frame.__init__(self, window, **kwargs)
		
		self.window = window
		
		self.model = None
		
		self.timer_id = None
		self.timer_total_reset_value = "00:00:00"
		
		self.config = configparser.ConfigParser()
		self.config.read("config.ini")
		
		self.utils = lib.utils.Utils()
		
		self.pack(expand = tkinter.YES, fill = tkinter.BOTH)
		
		menu_bar = tkinter.Menu(self.window)
		file_menu = tkinter.Menu(menu_bar, tearoff=0)
		file_menu.add_command(label = "Open", command = self.on_menu_file_open)
		file_menu.add_command(label = "Save", command = self.on_menu_file_save)
		menu_bar.add_cascade(label = "File", menu = file_menu)
		
		self.window.config(menu = menu_bar)
		
		frame_left = tkinter.Frame(self, width = 300)
		frame_left.pack_propagate(False)
		frame_left.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		frame_right = tkinter.Frame(self, width = 300)
		frame_right.pack_propagate(False)
		frame_right.pack(side = tkinter.RIGHT, fill = tkinter.BOTH)
		
		frame_cover = tkinter.LabelFrame(self, text = "Jaquette")
		frame_cover.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		frame_logo = tkinter.Frame(frame_left)
		frame_logo.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		frame_sheet = tkinter.LabelFrame(frame_left, text = "Gdoc")
		frame_sheet.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		frame_sheet_top = tkinter.Frame(frame_sheet)
		frame_sheet_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
		
		frame_run = tkinter.LabelFrame(frame_left, text = "Run")
		frame_run.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		frame_run_top = tkinter.Frame(frame_run)
		frame_run_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
		
		frame_run_bottom = tkinter.Frame(frame_run)
		frame_run_bottom.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		frame_sheet_labels = tkinter.Frame(frame_sheet_top)
		frame_sheet_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		frame_sheet_values = tkinter.Frame(frame_sheet_top)
		frame_sheet_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)
		
		frame_run_labels = tkinter.Frame(frame_run_top)
		frame_run_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		frame_run_values = tkinter.Frame(frame_run_top)
		frame_run_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)
		
		frame_scraper_game_info = tkinter.LabelFrame(frame_right, text = "Informations jeu")
		frame_scraper_game_info.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		frame_scraper_game_info_top = tkinter.Frame(frame_scraper_game_info)
		frame_scraper_game_info_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
		
		frame_scraper_game_info_top_labels = tkinter.Frame(frame_scraper_game_info_top)
		frame_scraper_game_info_top_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		frame_scraper_game_info_top_values = tkinter.Frame(frame_scraper_game_info_top)
		frame_scraper_game_info_top_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)
		
		frame_scraper_game_info_bottom = tkinter.Frame(frame_scraper_game_info)
		frame_scraper_game_info_bottom.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		frame_scraper_game_info_canvas = tkinter.Frame(frame_scraper_game_info)
		frame_scraper_game_info_canvas.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		pil_img = PIL.Image.open("resources/retrolection.png")
		self.img_logo = PIL.ImageTk.PhotoImage(pil_img) # reference to image must be kept to avoid garbage deletion
		canvas = tkinter.Canvas(frame_logo, width = self.img_logo.width(), height = self.img_logo.height())
		canvas.create_image((0, 0), anchor = tkinter.NW, image = self.img_logo)
		canvas.pack(side = tkinter.LEFT)
		
		self.combo_consoles = self.create_combo(frame_sheet_labels, frame_sheet_values, "Consoles: ", self.on_combo_consoles_changed)
		self.combo_games = self.create_combo(frame_sheet_labels, frame_sheet_values, "Jeux: ", self.on_combo_games_changed)
		self.entry_game_suffix = self.create_entry(frame_sheet_labels, frame_sheet_values, "Suffixe nom du jeu: ")
		self.label_progression_console = self.create_label(frame_sheet_labels, frame_sheet_values, "Progression console: ")
		self.label_progression_total = self.create_label(frame_sheet_labels, frame_sheet_values, "Progression totale: ")
		self.label_viewer_sub = self.create_label(frame_sheet_labels, frame_sheet_values, "Viewer sub: ")
		self.label_viewer_don = self.create_label(frame_sheet_labels, frame_sheet_values, "Viewer don: ")
		self.label_challenge_sub = self.create_label(frame_sheet_labels, frame_sheet_values, "Défi sub: ")
		self.label_challenge_don = self.create_label(frame_sheet_labels, frame_sheet_values, "Défi don: ")
		self.label_timer_game = self.create_label(frame_run_labels, frame_run_values, "Temps: ")
		self.label_timer_total = self.create_label(frame_run_labels, frame_run_values, "Total Retrolection: ")
		self.button_start_pause = self.create_button(frame_run_bottom, "Démarrer", self.on_start_pause_click)
		self.create_button(frame_run_bottom, "Remettre à zéro", self.on_reset_click)
		self.create_button(frame_run_bottom, "Valider", self.on_validate_click)
		self.create_button(frame_cover, "Charger...", self.on_cover_load_click)
		
		self.canvas_cover = lib.canvas_cover.CanvasCover(frame_cover)
		
		self.combo_scraper_games = self.create_combo(frame_scraper_game_info_top_labels, frame_scraper_game_info_top_values, "Titre trouvés: ", self.on_combo_scraper_games_changed)
		self.label_scraper_game_release_date = self.create_label(frame_scraper_game_info_top_labels, frame_scraper_game_info_top_values, "Date de sortie: ")
		self.label_scraper_game_players = self.create_label(frame_scraper_game_info_top_labels, frame_scraper_game_info_top_values, "Nombre de joueurs: ")
		self.label_scraper_game_alternates = self.create_label(frame_scraper_game_info_top_labels, frame_scraper_game_info_top_values, "Titre(s) alternatif(s): ")
		self.label_scraper_game_developers = self.create_label(frame_scraper_game_info_top_labels, frame_scraper_game_info_top_values, "Developpeur(s): ")
		self.label_scraper_game_publishers = self.create_label(frame_scraper_game_info_top_labels, frame_scraper_game_info_top_values, "Editeur(s): ")
		
		label = tkinter.Label(frame_scraper_game_info_top_labels, anchor = tkinter.W, text = "Jaquette: ")
		label.pack(anchor = tkinter.W)
		
		self.canvas_scraper_cover = lib.canvas_cover.CanvasCover(frame_scraper_game_info_canvas)
		
		self.create_button(frame_scraper_game_info_bottom, "<< Utiliser cette jaquette", self.on_use_this_cover_click)
		
	def create_combo(self, frame_label, frame_value, text, on_changed_cb):
		label = tkinter.Label(frame_label, anchor = tkinter.W, text = text)
		label.pack(anchor = tkinter.W, padx = 2, pady = 2)
		combo = tkinter.ttk.Combobox(frame_value, state = "readonly")
		combo.pack(padx = 2, pady = 2, fill = tkinter.X)
		combo.bind("<<ComboboxSelected>>", on_changed_cb)
		return combo
		
	def create_label(self, frame_label, frame_value, text):
		label = tkinter.Label(frame_label, anchor = tkinter.W, text = text)
		label.pack(anchor = tkinter.W, padx = 2, pady = 2)
		label_value = tkinter.Label(frame_value, anchor = tkinter.W)
		label_value.pack(anchor = tkinter.W, padx = 2, pady = 2)
		return label_value
		
	def create_entry(self, frame_label, frame_value, text):
		label = tkinter.Label(frame_label, anchor = tkinter.W, text = text)
		label.pack(anchor = tkinter.W, padx = 2, pady = 2)
		entry = tkinter.Entry(frame_value)
		entry.pack(fill = tkinter.X, padx = 2, pady = 2)
		return entry
		
	def create_button(self, frame, text, on_click_cb):
		button = tkinter.Button(frame, relief = tkinter.GROOVE, text = text, command = on_click_cb)
		button.pack(fill = tkinter.X, padx = 2, pady = 2)
		return button
		
	def get_combo_value(self, combo):
		current_index = combo.current()
		values = combo.cget("values")
		if current_index >= 0 and current_index < len(values):
			return values[current_index]
		return ""
		
	def select_combo_value(self, combo, value):
		values = combo.cget("values")
		
		i = 0
		for v in values:
			if v == value:
				combo.current(i)
				return True
			i += 1
			
		return False
		
	def on_menu_file_open(self):
		file_name = tkinter.filedialog.askopenfilename(defaultextension = "*.rcx", filetypes = [("Retrolection context files", "*.rcx")])
		if len(file_name) >= 1:
			self.load_context(file_name)
			
	def on_menu_file_save(self):
		file_name = tkinter.filedialog.asksaveasfilename(defaultextension = "*.rcx", filetypes = [("Retrolection context files", "*.rcx")])
		if len(file_name) >= 1:
			self.save_context(file_name)
			
	def on_use_this_cover_click(self):
		if self.canvas_scraper_cover.download_image(MainFrame.SCRAPER_COVER_FILE_NAME):
			self.canvas_cover.load_image(MainFrame.SCRAPER_COVER_FILE_NAME, True, MainFrame.RESIZED_COVER_FILE_NAME)
			
	def on_cover_load_click(self):
		file_name = tkinter.filedialog.askopenfilename()
		self.canvas_cover.load_image(file_name, True, MainFrame.RESIZED_COVER_FILE_NAME)
		
	def set_game_model_value(self, value_label, value):
		model_games = self.model["consoles"][self.get_combo_value(self.combo_consoles)]["games"]
		current_game_index = self.combo_games.current()
		model_games[current_game_index][value_label] = value
		
	def set_time(self, time_str):
		self.set_game_model_value("timer", time_str)
		self.label_timer_game.config(text = time_str)
		self.utils.write_file("w", "text-files/timer-game.txt", time_str)
		
	def set_total_time(self, time_str):
		self.model["timer_total"] = time_str
		self.label_timer_total.config(text = time_str)
		self.utils.write_file("w", "text-files/timer-total.txt", time_str)
		
	def start_timer(self):
		if self.timer_id:
			self.window.after_cancel(self.timer_id)
		self.timer_id = self.window.after(1000, self.update_timer)
		
	def stop_timer(self):
		if self.timer_id:
			self.window.after_cancel(self.timer_id)
			self.timer_id = None
			
	def start_run(self):
		self.button_start_pause.config(text = "Pause")
		self.utils.write_file("w", "text-files/game.txt", self.combo_games.cget("values")[self.combo_games.current()] + self.entry_game_suffix.get())
		self.utils.write_file("w", "text-files/progression-console.txt", self.label_progression_console.cget("text"))
		self.utils.write_file("w", "text-files/progression-total.txt", self.label_progression_total.cget("text"))
		self.utils.write_file("w", "text-files/viewer-sub.txt", self.label_viewer_sub.cget("text"))
		self.utils.write_file("w", "text-files/viewer-don.txt", self.label_viewer_don.cget("text"))
		self.utils.write_file("w", "text-files/challenge-sub.txt", self.label_challenge_sub.cget("text"))
		self.utils.write_file("w", "text-files/challenge-don.txt", self.label_challenge_don.cget("text"))
		self.utils.write_file("w", "text-files/timer-game.txt", self.label_timer_game.cget("text"))
		self.utils.write_file("w", "text-files/timer-total.txt", self.label_timer_total.cget("text"))
		
		if not self.canvas_cover.has_image():
			self.utils.copy_file("default-cover.png", "img-files/cover.png")
		else:
			self.utils.copy_file(MainFrame.RESIZED_COVER_FILE_NAME, "img-files/cover.png")
		
		self.start_timer()
		
	def pause_run(self):
		self.button_start_pause.config(text = "Démarrer")
		self.stop_timer()
		
	def on_start_pause_click(self):
		if self.button_start_pause.cget("text") == "Démarrer":
			self.start_run()
		else:
			self.pause_run()
			self.save_game_to_sheet()
		
	def on_reset_click(self):
		self.pause_run()
		self.set_time("00:00:00")
		self.set_total_time(self.timer_total_reset_value)
		self.save_game_to_sheet()
		
	def on_validate_click(self):
		self.pause_run()
		self.save_game_to_sheet()
		
		model_console = self.model["consoles"][self.get_combo_value(self.combo_consoles)]
		model_games = model_console["games"]
		current_game_index = self.combo_games.current()
		model_game = model_games[current_game_index]
		if model_game["original_timer"] == None:
			value, total = self.utils.progressStrToValues(self.model["progression_total"])
			s = self.utils.progressValuesToStr(value + 1, total)
			self.model["progression_total"] = s
			self.label_progression_total.config(text = s)
			self.utils.write_file("w", "text-files/progression-total.txt", s)
			
			value, total = self.utils.progressStrToValues(model_console["progression"])
			s = self.utils.progressValuesToStr(value + 1, total)
			model_console["progression"] = s
			self.label_progression_console.config(text = s)
			self.utils.write_file("w", "text-files/progression-console.txt", s)
			
			model_game["original_timer"] = model_game["timer"]
			
	def save_game_to_sheet(self):
		console = self.get_combo_value(self.combo_consoles)
		model_games = self.model["consoles"][console]["games"]
		current_game_index = self.combo_games.current()
		
		config_sheet = self.config["SHEET"]
		sheet_name = console
		line = str(int(config_sheet["FIRST_GAME_LINE"]) + current_game_index)
		ranges_values = [
			{
				"range": sheet_name + "!" + config_sheet["TIMER_GAME_COLUMN"] + line + ":" + config_sheet["TIMER_GAME_COLUMN"] + line,
				"values": [[model_games[current_game_index]["timer"]]]
			},
		]
		
		self.sheets_client.set_values(ranges_values)
		
	def update_timer(self):
		t = self.utils.timeStrToSec(self.label_timer_game.cget("text"))
		t += 1
		self.set_time(self.utils.timeSecToStr(t))
		
		t = self.utils.timeStrToSec(self.label_timer_total.cget("text"))
		t += 1
		self.set_total_time(self.utils.timeSecToStr(t))
		
		self.timer_id = self.window.after(1000, self.update_timer)
		
		
	def on_timer_reset_click(self):
		self.label_timer_game.config(text = "00:00:00")
		self.label_timer_total.config(text = self.timer_total_reset_value)
		
	def on_combo_consoles_changed(self, event):
		self.process_on_combo_consoles_changed()
		
	def fill_consoles(self):
		values = []
		
		for value in self.model["consoles"]:
			values.append(value)
		
		self.combo_consoles.config(values = values)
		self.combo_consoles.current(0)
		
		self.process_on_combo_consoles_changed()
		
	def process_on_combo_consoles_changed(self):
		self.fill_games()
		self.label_progression_console.config(text = self.model["consoles"][self.get_combo_value(self.combo_consoles)]["progression"])
		
	def on_combo_games_changed(self, event):
		self.process_on_combo_games_changed()
		
	def fill_games(self):
		values = []
		
		for value in self.model["consoles"][self.get_combo_value(self.combo_consoles)]["games"]:
			values.append(value["name"])
			
		self.combo_games.config(values = values)
		self.combo_games.current(0)
		
		self.process_on_combo_games_changed()
		
	def process_on_combo_games_changed(self):
		model_games = self.model["consoles"][self.get_combo_value(self.combo_consoles)]["games"]
		current_game_index = self.combo_games.current()
		
		self.label_viewer_sub.config(text = model_games[current_game_index]["viewer_sub"])
		self.label_viewer_don.config(text = model_games[current_game_index]["viewer_don"])
		self.label_challenge_sub.config(text = model_games[current_game_index]["challenge_sub"])
		self.label_challenge_don.config(text = model_games[current_game_index]["challenge_don"])
		self.label_timer_game.config(text = model_games[current_game_index]["timer"])
		
		self.timer_total_reset_value = self.utils.timeSecToStr(self.utils.timeStrToSec(self.model["timer_total"]) - self.utils.timeStrToSec(model_games[current_game_index]["timer"]))
		
		self.fill_scraper_games()
		
	def on_combo_scraper_games_changed(self, event):
		self.process_on_combo_scraper_games_changed()
		
	def fill_scraper_games(self):
		try:
			console = self.get_combo_value(self.combo_consoles)
			game = self.get_combo_value(self.combo_games)
			
			found_games = self.games_db_client.search_game_by_name(game, console)
			
			value_to_id = {}
			values = []
			
			for v in found_games:
				values.append(v["title"])
				value_to_id[v["title"]] = v["id"]
				
			self.combo_scraper_games.set("")
			
			self.combo_scraper_games.value_to_id = value_to_id
			self.combo_scraper_games.config(values = values)
			
			if len(values) >= 1:
				self.combo_scraper_games.current(0)
			
			self.process_on_combo_scraper_games_changed()
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			
	def process_on_combo_scraper_games_changed(self):
		image_path = None
		if self.combo_scraper_games.current() >= 0:
			scraper_game = self.combo_scraper_games.cget("values")[self.combo_scraper_games.current()]
			
			info = self.games_db_client.get_game_info(self.combo_scraper_games.value_to_id[scraper_game])
			
			self.label_scraper_game_release_date.config(text = info["release_date"])
			players_str = str(info["players"]) + " (Co-op: " + info["coop"] + ")"
			self.label_scraper_game_players.config(text = players_str)
			self.label_scraper_game_alternates.config(text = info["alternates"])
			self.label_scraper_game_developers.config(text = info["developers"])
			self.label_scraper_game_publishers.config(text = info["publishers"])
			
			image_path = info["url_image"]
			
		self.canvas_scraper_cover.load_image(image_path, False, None)
		
	def set_sheet_data_simple_values_to_model(self, data, model_games, game_start_row, field_name):
		id = data["startRow"] - game_start_row
		for row_data in data["rowData"]:
			if id >= 0 and id < len(model_games):
				if "values" in row_data and "formattedValue" in row_data["values"][0]:
					model_games[id][field_name] = row_data["values"][0]["formattedValue"]
			id += 1
			
	def set_sheet_data_challenge_values_to_model(self, data, model_games, game_start_row, field_name):
		id = data["startRow"] - game_start_row
		if "rowData" not in data:
			return
		for row_data in data["rowData"]:
			if id >= 0 and id < len(model_games):
				if "values" in row_data:
					values = row_data["values"]
					
					# Find the first value with a green background color
					for value in values:
						if "formattedValue" in value \
						and "userEnteredFormat" in value \
						and "backgroundColor" in value["userEnteredFormat"]:
							background_color = value["userEnteredFormat"]["backgroundColor"]
							
							red = 0
							green = 0
							blue = 0
							if "red" in background_color:
								red = background_color["red"];
							if "green" in background_color:
								green = background_color["green"];
							if "blue" in background_color:
								blue = background_color["blue"];
								
							if red == 0 and green == 1 and blue == 0:
								model_games[id][field_name] = value["formattedValue"]
								break
			id += 1
			
	def set_sheet_data_simple_value_to_model(self, data, model_console, field_name):
		row_data = data["rowData"][0]
		if "values" in row_data and "formattedValue" in row_data["values"][0]:
			model_console[field_name] = row_data["values"][0]["formattedValue"]
			
	def set_sheet_data_progression_value_to_model(self, data, model_console, field_name):
		if "rowData" in data:
			row_data = data["rowData"][0]
			if "values" in row_data and "formattedValue" in row_data["values"][0] and "formattedValue" in row_data["values"][2]:
				nb_completed = int(row_data["values"][0]["formattedValue"])
				nb_total = int(row_data["values"][2]["formattedValue"])
				model_console[field_name] = self.utils.progressValuesToStr(nb_completed, nb_total)
				return nb_completed, nb_total
				
		return 0, 0
		
	def build_model(self):
		model = {
			"timer_total": "00:00:00",
			"progression_total": "",
			"consoles": {},
		}
		
		config_sheet = self.config["SHEET"]
		
		response = self.sheets_client.get_sheets()
		
		if response["sheets"]:
			start_index = int(config_sheet["FIRST_GAME_CONSOLE_SHEET"]) - 1
			for i in range(start_index, start_index + int(config_sheet["NUMBER_OF_GAME_CONSOLE_SHEETS"])):
				item = response["sheets"][i];
				if item["properties"] and item["properties"]["title"]:
					model["consoles"][item["properties"]["title"]] = {
						"games": [],
						"progression": "",
						"timer_total": "00:00:00",
					}
					
		first_line = config_sheet["FIRST_GAME_LINE"]
		
		ranges = []
		
		for console in model["consoles"]:
			ranges.append(console + "!" + config_sheet["GAME_NAME_COLUMN"] + first_line + ":" + config_sheet["GAME_NAME_COLUMN"])
			ranges.append(console + "!" + config_sheet["TIMER_GAME_COLUMN"] + first_line + ":" + config_sheet["TIMER_GAME_COLUMN"])
			ranges.append(console + "!" + config_sheet["VIEWER_SUB_COLUMN"] + first_line + ":" + config_sheet["VIEWER_SUB_COLUMN"])
			ranges.append(console + "!" + config_sheet["VIEWER_DON_COLUMN"] + first_line + ":" + config_sheet["VIEWER_DON_COLUMN"])
			ranges.append(console + "!" + config_sheet["CHALLENGE_SUB_COLUMN"] + first_line + ":" + config_sheet["CHALLENGE_SUB_COLUMN"])
			ranges.append(console + "!" + config_sheet["CHALLENGE_DON_FIRST_COLUMN"] + first_line + ":" + config_sheet["CHALLENGE_DON_LAST_COLUMN"])
			ranges.append(console + "!" + config_sheet["PROGRESSION_CELL_RANGE"])
			ranges.append(console + "!" + config_sheet["TIMER_TOTAL_CELL"] + ":" + config_sheet["TIMER_TOTAL_CELL"])
			
		values = self.sheets_client.get_values(ranges)
		
		sheets = values["sheets"]
		
		nb_games_completed = 0
		nb_games_total = 0
		
		for sheet in sheets:
			console = sheet["properties"]["title"]
			
			data = sheet["data"]
			
			# Find game column
			game_data = None
			game_start_row = None
			for d in data:
				if "startColumn" in d \
				and d["startColumn"] == self.utils.sheet_a1_value_to_column_number(config_sheet["GAME_NAME_COLUMN"]):
					game_data = d
					game_start_row = d["startRow"]
					break
					
			for r in game_data["rowData"]:
				if "formattedValue" in r["values"][0]:
					model["consoles"][console]["games"].append({
						"name": r["values"][0]["formattedValue"],
						"original_timer": None,
						"timer": "00:00:00",
						"viewer_sub": "",
						"viewer_don": "",
						"challenge_sub": "",
						"challenge_don": "",
					})
					
			for d in data:
				if "startColumn" in d:
					column = d["startColumn"]
				else:
					column = 0
					
				if column == self.utils.sheet_a1_value_to_column_number(config_sheet["TIMER_GAME_COLUMN"]):
					self.set_sheet_data_simple_values_to_model(d, model["consoles"][console]["games"], game_start_row, "original_timer")
					self.set_sheet_data_simple_values_to_model(d, model["consoles"][console]["games"], game_start_row, "timer")
				elif column == self.utils.sheet_a1_value_to_column_number(config_sheet["VIEWER_SUB_COLUMN"]):
					self.set_sheet_data_simple_values_to_model(d, model["consoles"][console]["games"], game_start_row, "viewer_sub")
				elif column == self.utils.sheet_a1_value_to_column_number(config_sheet["VIEWER_DON_COLUMN"]):
					self.set_sheet_data_simple_values_to_model(d, model["consoles"][console]["games"], game_start_row, "viewer_don")
				elif column == self.utils.sheet_a1_value_to_column_number(config_sheet["CHALLENGE_SUB_COLUMN"]):
					self.set_sheet_data_challenge_values_to_model(d, model["consoles"][console]["games"], game_start_row, "challenge_sub")
				elif column == self.utils.sheet_a1_value_to_column_number(config_sheet["CHALLENGE_DON_FIRST_COLUMN"]):
					self.set_sheet_data_challenge_values_to_model(d, model["consoles"][console]["games"], game_start_row, "challenge_don")
				elif column == self.utils.sheet_a1_value_to_column_number(config_sheet["PROGRESSION_CELL_RANGE"]):
					nb_completed, nb_total = self.set_sheet_data_progression_value_to_model(d, model["consoles"][console], "progression")
					nb_games_completed += nb_completed
					nb_games_total += nb_total
				elif column == self.utils.sheet_a1_value_to_column_number(config_sheet["TIMER_TOTAL_CELL"]):
					self.set_sheet_data_simple_value_to_model(d, model["consoles"][console], "timer_total")
					
		t = 0
		for console in model["consoles"]:
			t += self.utils.timeStrToSec(model["consoles"][console]["timer_total"])
			
		model["timer_total"] = self.utils.timeSecToStr(t)
		
		model["progression_total"] = self.utils.progressValuesToStr(nb_games_completed, nb_games_total)
			
		return model
		
	def load(self):
		if not os.path.isfile(MainFrame.TOKENS_FILENAME):
			tkinter.messagebox.showerror("Error", " File "+ MainFrame.TOKENS_FILENAME +" not found. Please run grant_permissions.bat.")
			sys.exit()
			
		self.games_db_client = lib.games_db_client.GamesDbClient(self.config["DATA_BASES"]["THE_GAMES_DB_API_KEY"])
		self.sheets_client = lib.sheets_client.SheetsClient(self.config["SHEET"]["GDOC_API_KEY"], self.config["SHEET"]["OAUTH_CLIENT_ID"], self.config["SHEET"]["OAUTH_CLIENT_SECRET"], self.config["SHEET"]["SPREAD_SHEET_ID"], MainFrame.TOKENS_FILENAME)
		self.model = self.build_model()
		self.label_timer_total.config(text = self.model["timer_total"])
		self.label_progression_total.config(text = self.model["progression_total"])
		self.fill_consoles()
		
		ret = self.load_context("context.sav")
		
		if ret == False:
			self.process_on_combo_consoles_changed()
			
	def load_context(self, file_name):
		ret = False
		if os.path.exists(file_name):
			config = configparser.ConfigParser()
			config.read(file_name)
			
			if self.select_combo_value(self.combo_consoles, config["CONTEXT"]["console"]):
				self.process_on_combo_consoles_changed()
				ret = True
				
				if self.select_combo_value(self.combo_games, config["CONTEXT"]["game"]):
					self.process_on_combo_games_changed()
					
				if "cover" in config["CONTEXT"]:
					self.canvas_cover.load_image(config["CONTEXT"]["cover"], True, MainFrame.RESIZED_COVER_FILE_NAME)
					
			if "game_suffix" in config["CONTEXT"]:
				self.entry_game_suffix.delete(0, tkinter.END)
				self.entry_game_suffix.insert(0, config["CONTEXT"]["game_suffix"].replace("<SPACE>", " "))
				
		return ret
		
	def save_context(self, file_name):
		config = configparser.ConfigParser()
		
		config["CONTEXT"] = {
			"console": self.get_combo_value(self.combo_consoles),
			"game": self.get_combo_value(self.combo_games),
			"game_suffix": self.entry_game_suffix.get().replace(" ", "<SPACE>")
		}
		
		image_path = self.canvas_cover.get_image_path()
		if image_path:
			config["CONTEXT"]["cover"] = image_path
			
		with open(file_name, "w") as f:
			config.write(f)
		
	def on_close(self):
		self.save_context("context.sav")
		try:
			self.window.destroy()
		except:
			pass
			
def main():
	window = tkinter.Tk()
	window.title("Retrolection")
	window.geometry("1050x600")
	window.geometry(("+" + str(int((window.winfo_screenwidth() - 1050) / 2)) + "+"+ str(int((window.winfo_screenheight() - 600) / 2))))
	f = MainFrame(window)
	window.protocol("WM_DELETE_WINDOW", f.on_close)
	icon = tkinter.PhotoImage(file = "resources/icon.png")
	window.tk.call("wm", "iconphoto", window._w, icon)
	window.after(1, f.load)
	window.mainloop()
	
if __name__ == "__main__":
	main()
	
