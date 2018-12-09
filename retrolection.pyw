
import time
import configparser
import urllib
import urllib.request
import json
import shutil
import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk


class MainFrame(tkinter.Frame):

	def __init__(self, window, **kwargs):
		tkinter.Frame.__init__(self, window, **kwargs)
		
		self.window = window
		self.pil_cover = None
		self.timer_id = None
		self.timer_total_reset_value = "00:00:00"
		
		self.config = configparser.ConfigParser()
		self.config.read("config.ini")
		
		self.pack(expand = tkinter.YES, fill = tkinter.BOTH)
		
		self.frame_left = tkinter.Frame(self, width = 300)
		self.frame_left.pack_propagate(False)
		self.frame_left.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		self.frame_cover = tkinter.LabelFrame(self, text = "Jaquette")
		self.frame_cover.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		self.frame_logo = tkinter.Frame(self.frame_left)
		self.frame_logo.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		self.frame_sheet = tkinter.LabelFrame(self.frame_left, text = "Gdoc")
		self.frame_sheet.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		self.frame_sheet_top = tkinter.Frame(self.frame_sheet)
		self.frame_sheet_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
		
		self.frame_sheet_bottom = tkinter.Frame(self.frame_sheet)
		self.frame_sheet_bottom.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		self.frame_timer = tkinter.LabelFrame(self.frame_left, text = "Timer")
		self.frame_timer.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		self.frame_timer_top = tkinter.Frame(self.frame_timer)
		self.frame_timer_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
		
		self.frame_timer_bottom = tkinter.Frame(self.frame_timer)
		self.frame_timer_bottom.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		self.frame_sheet_labels = tkinter.Frame(self.frame_sheet_top)
		self.frame_sheet_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		self.frame_sheet_values = tkinter.Frame(self.frame_sheet_top)
		self.frame_sheet_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)
		
		self.frame_timer_labels = tkinter.Frame(self.frame_timer_top)
		self.frame_timer_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		self.frame_timer_values = tkinter.Frame(self.frame_timer_top)
		self.frame_timer_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)
		
		pil_img = PIL.Image.open("resources/retrolection.png")
		self.img_logo = PIL.ImageTk.PhotoImage(pil_img) # reference to image must be kept to avoid garbage deletion
		canvas = tkinter.Canvas(self.frame_logo, width = self.img_logo.width(), height = self.img_logo.height())
		canvas.create_image((0, 0), anchor = tkinter.NW, image = self.img_logo)
		canvas.pack(side = tkinter.LEFT)
		
		label = tkinter.Label(self.frame_sheet_labels, text = "Consoles: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.combo_consoles = tkinter.ttk.Combobox(self.frame_sheet_values, state = "readonly")
		self.combo_consoles.pack(padx = 5, pady = 5, fill = tkinter.X)
		self.combo_consoles.bind("<<ComboboxSelected>>", self.on_combo_consoles_changed)
		
		label = tkinter.Label(self.frame_sheet_labels, text = "Jeux: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.combo_games = tkinter.ttk.Combobox(self.frame_sheet_values, state = "readonly")
		self.combo_games.pack(padx = 5, pady = 5, fill = tkinter.X)
		self.combo_games.bind("<<ComboboxSelected>>", self.on_combo_games_changed)
		
		label = tkinter.Label(self.frame_sheet_labels, text = "Progression: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_progress = tkinter.Label(self.frame_sheet_values)
		self.label_progress.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, text = "Viewer sub: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_viewer_sub = tkinter.Label(self.frame_sheet_values)
		self.label_viewer_sub.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, text = "Viewer don: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_viewer_don = tkinter.Label(self.frame_sheet_values)
		self.label_viewer_don.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, text = "Défi sub: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_challenge_sub = tkinter.Label(self.frame_sheet_values)
		self.label_challenge_sub.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, text = "Défi don: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_challenge_don = tkinter.Label(self.frame_sheet_values)
		self.label_challenge_don.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		button = tkinter.Button(self.frame_sheet_bottom, relief = tkinter.GROOVE, text = "Envoyer les valeurs vers XSplit", command = self.on_update_xsplit_click)
		button.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_timer_labels, text = "Jeu en cours: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_timer_game = tkinter.Label(self.frame_timer_values)
		self.label_timer_game.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_timer_labels, text = "Total Retrolection: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_timer_total = tkinter.Label(self.frame_timer_values)
		self.label_timer_total.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		self.button_timer_action = tkinter.Button(self.frame_timer_bottom, relief = tkinter.GROOVE, text = "Start", command = self.on_timer_action_click)
		self.button_timer_action.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		button = tkinter.Button(self.frame_timer_bottom, relief = tkinter.GROOVE, text = "Reset timer du jeu", command = self.on_timer_reset_click)
		button.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		button = tkinter.Button(self.frame_cover, relief = tkinter.GROOVE, text = "Charger...", command = self.on_cover_load_click)
		button.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		self.canvas_cover = tkinter.Canvas(self.frame_cover, bg = "black")
		self.canvas_cover.pack(expand = tkinter.YES, fill = tkinter.BOTH)
		self.canvas_cover.bind("<Configure>", self.canvas_cover_configure)
		
	def canvas_cover_configure(self, event):
		self.refresh_cover(event.width, event.height)
		
	def on_update_xsplit_click(self):
		self.write_file("w", "text-files/game.txt", self.combo_games.cget("values")[self.combo_games.current()])
		self.write_file("w", "text-files/progression.txt", self.label_progress.cget("text"))
		self.write_file("w", "text-files/viewer-sub.txt", self.label_viewer_sub.cget("text"))
		self.write_file("w", "text-files/viewer-don.txt", self.label_viewer_don.cget("text"))
		self.write_file("w", "text-files/challenge-sub.txt", self.label_challenge_sub.cget("text"))
		self.write_file("w", "text-files/challenge-don.txt", self.label_challenge_don.cget("text"))
		self.write_file("w", "text-files/timer-game.txt", self.label_timer_game.cget("text"))
		self.write_file("w", "text-files/timer-total.txt", self.label_timer_total.cget("text"))
		
		if not self.pil_cover:
			self.copy_file("default-cover.png", "img-files/cover.png")
		else:
			self.copy_file("cover.png", "img-files/cover.png")
		
	def on_cover_load_click(self):
		file_name = tkinter.filedialog.askopenfilename()
		if file_name:
			try:
				self.pil_cover = PIL.Image.open(file_name)
			except:
				tkinter.messagebox.showerror("Error", "Image " + file_name + " cannot be loaded.")
				self.pil_cover = None
				
			if self.pil_cover:
				pil_cover_resized = self.resize_image(self.pil_cover, 400, 400)
				pil_cover_resized_width, pil_cover_resized_height = pil_cover_resized.size
				image = PIL.Image.new('RGB', (400, 400), (0, 0, 0))
				image.paste(pil_cover_resized, ((400 - pil_cover_resized_width) // 2, (400 - pil_cover_resized_height) // 2))
				image.save("cover.png")
				
			self.refresh_cover(self.canvas_cover.winfo_width(), self.canvas_cover.winfo_height())
			
	def timer_action_start(self):
		self.button_timer_action.config(text = "Stop")
		if self.timer_id:
			self.window.after_cancel(self.timer_id)
		self.timer_id = self.window.after(1000, self.update_timers)
		
	def timer_action_stop(self):
		if self.timer_id:
			self.window.after_cancel(self.timer_id)
			self.timer_id = None
		self.button_timer_action.config(text = "Start")
		
	def on_timer_action_click(self):
		if self.button_timer_action.cget("text") == "Start":
			self.timer_action_start()
		else:
			self.timer_action_stop()
			
	def on_timer_reset_click(self):
		self.label_timer_game.config(text = "00:00:00")
		self.label_timer_total.config(text = self.timer_total_reset_value)
		
	def timeStrToSec(self, t):
		v = t.split(":")
		
		if len(v) >= 3:
			val = int(v[0]) * 3600 + int(v[1]) * 60 + int(v[2])
		elif len(v) >= 2:
			val = int(v[0]) * 60 + int(v[1])
		else:
			val = int(v[0])
			
		return val
		
	def timeSecToStr(self, t):
		h = str(t // 3600)
		if len(h) < 2:
			h = "0" + h
		m = ("0" + str((t % 3600) // 60))[-2:]
		s = ("0" + str(t % 60))[-2:]
		return h + ":" + m + ":" + s
		
	def update_timers(self):
		t = self.timeStrToSec(self.label_timer_game.cget("text"))
		t += 1
		s = self.timeSecToStr(t)
		self.label_timer_game.config(text = s)
		self.write_file("w", "text-files/timer-game.txt", s)
		
		t = self.timeStrToSec(self.label_timer_total.cget("text"))
		t += 1
		s = self.timeSecToStr(t)
		self.label_timer_total.config(text = s)
		self.write_file("w", "text-files/timer-total.txt", s)
		
		self.timer_id = self.window.after(1000, self.update_timers)
		
	def resize_image(self, image, width, height):
		img_width, img_height = image.size
		ratio = img_width / img_height
		if img_height < img_width:
			new_width = width - 10
			new_height = int(new_width / ratio)
		else:
			new_height = height - 10
			new_width = int(new_height * ratio)
			
		return image.resize((new_width, new_height), PIL.Image.ANTIALIAS)
		
	def refresh_cover(self, canvas_width, canvas_height):
		if not self.pil_cover:
			self.canvas_cover.delete("all")
		else:
			pil_cover_resized = self.resize_image(self.pil_cover, canvas_width, canvas_height)
			self.img_cover = PIL.ImageTk.PhotoImage(pil_cover_resized) # reference to image must be kept to avoid garbage deletion
			self.canvas_cover.create_image((canvas_width // 2, canvas_height // 2), image = self.img_cover)
			
	def get_json(self, url):
		request = urllib.request.Request(url)
		response = urllib.request.urlopen(request).read()
		return json.loads(response.decode('utf-8'))
		
	def get_sheet_values(self, sheet_name, cell_range):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/values/" + urllib.parse.quote(sheet_name) + "!" + cell_range + "/?key=" + self.config["SHEET"]["API_KEY"];
		data = self.get_json(url)
		
		if "values" not in data:
			return None
		else:
			return data["values"]
			
	def get_sheet_properties(self, sheet_name, cell_range):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/?key=" + self.config["SHEET"]["API_KEY"] + "&ranges=" + urllib.parse.quote(sheet_name) + "!" + cell_range + "&includeGridData=true";
		data = self.get_json(url)
		
		return data["sheets"][0]["data"][0]["rowData"][0]["values"]
		
	def on_combo_consoles_changed(self, event):
		self.process_on_combo_consoles_changed()
		
	def on_combo_games_changed(self, event):
		self.process_on_combo_games_changed()
		
	def process_on_combo_consoles_changed(self):
		self.fill_games()
		self.fill_progress()
		
	def process_on_combo_games_changed(self):
		self.fill_viewer_sub()
		self.fill_viewer_don()
		self.fill_challenge_sub()
		self.fill_challenge_don()
		self.fill_timers()
		
	def fill_consoles(self):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "?key=" + self.config["SHEET"]["API_KEY"]
		
		data = self.get_json(url)
		
		values = []
		
		if data["sheets"]:
			start_index = int(self.config["SHEET"]["FIRST_GAME_CONSOLE_SHEET"]) - 1
			for i in range(start_index, start_index + int(self.config["SHEET"]["NUMBER_OF_GAME_CONSOLE_SHEET"])):
				item = data["sheets"][i];
				if item["properties"] and item["properties"]["title"]:
					values.append(item["properties"]["title"])
					
		self.combo_consoles.config(values = values)
		self.combo_consoles.current(0)
		
		self.process_on_combo_consoles_changed()
		
	def fill_games(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		cell_range = self.config["SHEET"]["GAME_NAME_COLUMN"] + self.config["SHEET"]["FIRST_GAME_LINE"] + ":" + self.config["SHEET"]["TIMER_GAME_COLUMN"] + "1000"
		sheet_values = self.get_sheet_values(console, cell_range)
		
		values = []
		
		if sheet_values:
			for v in sheet_values:
				if v[0] and v[0] != "":
					values.append(v[0])
					
		self.combo_games.config(values = values)
		self.combo_games.current(0)
		
		self.process_on_combo_games_changed()
		
	def fill_progress(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		cell_range = self.config["SHEET"]["PROGRESSION_CELL_RANGE"]
		sheet_values = self.get_sheet_values(console, cell_range)
		
		self.label_progress.config(text = sheet_values[0][0] + "/" + sheet_values[0][2])
		
	def fill_viewer_sub(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		game_id = int(self.config["SHEET"]["FIRST_GAME_LINE"]) + self.combo_games.current()
		cell = self.config["SHEET"]["VIEWER_SUB_COLUMN"] + str(game_id)
		sheet_values = self.get_sheet_values(console, cell + ":" + cell)
		
		value = ""
		
		if sheet_values and sheet_values[0] and sheet_values[0][0]:
			value = sheet_values[0][0]
			
		self.label_viewer_sub.config(text = value)
		
	def fill_viewer_don(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		game_id = int(self.config["SHEET"]["FIRST_GAME_LINE"]) + self.combo_games.current()
		cell = self.config["SHEET"]["VIEWER_DON_COLUMN"] + str(game_id)
		sheet_values = self.get_sheet_values(console, cell + ":" + cell)
		
		value = ""
		
		if sheet_values and sheet_values[0] and sheet_values[0][0]:
			value = sheet_values[0][0]
			
		self.label_viewer_don.config(text = value)
		
	def get_selected_challenge(self, properties):
		for p in properties:
			if "userEnteredFormat" in p:
				if "backgroundColor" in p["userEnteredFormat"]:
					background_color = p["userEnteredFormat"]["backgroundColor"]
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
						return p["formattedValue"]
					
		return ""
		
	def fill_challenge_sub(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		game_id = int(self.config["SHEET"]["FIRST_GAME_LINE"]) + self.combo_games.current()
		cell = self.config["SHEET"]["CHALLENGE_SUB_COLUMN"] + str(game_id)
		sheet_properties = self.get_sheet_properties(console, cell + ":" + cell)
		
		selected_challenge = self.get_selected_challenge(sheet_properties)
		
		self.label_challenge_sub.config(text = selected_challenge)
		
	def fill_challenge_don(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		game_id = int(self.config["SHEET"]["FIRST_GAME_LINE"]) + self.combo_games.current()
		cell_range = self.config["SHEET"]["CHALLENGE_DON_FIRST_COLUMN"] + str(game_id) + ":" + self.config["SHEET"]["CHALLENGE_DON_LAST_COLUMN"] + str(game_id)
		sheet_properties = self.get_sheet_properties(console, cell_range)
		
		selected_challenge = self.get_selected_challenge(sheet_properties)
		
		self.label_challenge_don.config(text = selected_challenge)
		
	def fill_timers(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		game_id = int(self.config["SHEET"]["FIRST_GAME_LINE"]) + self.combo_games.current()
		cell = self.config["SHEET"]["TIMER_GAME_COLUMN"] + str(game_id)
		sheet_values = self.get_sheet_values(console, cell + ":" + cell)
		
		game_time = "00:00:00"
		
		if sheet_values and sheet_values[0] and sheet_values[0][0]:
			game_time = sheet_values[0][0]
			game_time = self.timeSecToStr(self.timeStrToSec(game_time))
			
		self.timer_action_stop()
		self.label_timer_game.config(text = game_time)
		
		
		consoles = self.combo_consoles.cget("values")
		
		ranges = ""
		for c in consoles:
			ranges += "&ranges=" + urllib.parse.quote(c) + "!" + self.config["SHEET"]["TIMER_TOTAL_CELL"] + ":" + self.config["SHEET"]["TIMER_TOTAL_CELL"]
				
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/values:batchGet?key=" + self.config["SHEET"]["API_KEY"] + ranges;
		
		data = self.get_json(url)
		
		t = 0
		for v in data["valueRanges"]:
			t += self.timeStrToSec(v["values"][0][0])
		
		self.label_timer_total.config(text = self.timeSecToStr(t))
		
		self.timer_total_reset_value = self.timeSecToStr(t - self.timeStrToSec(game_time))
		
		
	def write_file(self, mode, file_name, value):
		nb_retries = 0
		while nb_retries < 5:
			try:
				with open(file_name, mode) as f:
					f.write(value)
				break
			except:
				nb_retries += 1
				time.sleep(0.01)
				
	def copy_file(self, src_file_name, dst_file_name):
		nb_retries = 0
		while nb_retries < 5:
			try:
				shutil.copyfile(src_file_name, dst_file_name)
				break
			except:
				nb_retries += 1
				time.sleep(0.01)
				
def main():
	window = tkinter.Tk()
	window.title("Retrolection")
	window.geometry("800x600")
	window.geometry(("+" + str(int((window.winfo_screenwidth() - 800) / 2)) + "+"+ str(int((window.winfo_screenheight() - 600) / 2))))
	f = MainFrame(window)
	icon = tkinter.PhotoImage(file = "resources/icon.png")
	window.tk.call("wm", "iconphoto", window._w, icon)
	window.after(1, f.fill_consoles)
	window.mainloop()
	
if __name__ == "__main__":
	main()
	
