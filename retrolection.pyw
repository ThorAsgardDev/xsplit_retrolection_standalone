
import time
import configparser
import urllib.request
import json
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
		
		button = tkinter.Button(self.frame_sheet_bottom, relief = tkinter.GROOVE, text = "Envoyer les valeurs vers XSplit", command = self.on_update_xsplit_click)
		button.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_timer_labels, text = "Valeur: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_timer = tkinter.Label(self.frame_timer_values)
		self.label_timer.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		self.button_timer_action = tkinter.Button(self.frame_timer_bottom, relief = tkinter.GROOVE, text = "Start", command = self.on_timer_action_click)
		self.button_timer_action.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		button = tkinter.Button(self.frame_timer_bottom, relief = tkinter.GROOVE, text = "Reset", command = self.on_timer_reset_click)
		button.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		button = tkinter.Button(self.frame_cover, relief = tkinter.GROOVE, text = "Charger...", command = self.on_cover_load_click)
		button.pack(fill = tkinter.X, padx = 5, pady = 5)
		self.canvas_cover = tkinter.Canvas(self.frame_cover, bg = "black")
		self.canvas_cover.pack(expand = tkinter.YES, fill = tkinter.BOTH)
		self.canvas_cover.bind("<Configure>", self.canvas_cover_configure)
		
	def canvas_cover_configure(self, event):
		self.refresh_cover(event.width, event.height)
		
	def on_update_xsplit_click(self):
		self.write_file("text-files/game.txt", self.combo_games.cget("values")[self.combo_games.current()])
		self.write_file("text-files/progression.txt", self.label_progress.cget("text"))
		self.write_file("text-files/viewer-sub.txt", self.label_viewer_sub.cget("text"))
		self.write_file("text-files/viewer-don.txt", self.label_viewer_don.cget("text"))
		self.write_file("text-files/timer.txt", self.label_timer.cget("text"))
		
	def on_cover_load_click(self):
		file_name = tkinter.filedialog.askopenfilename()
		if file_name:
			try:
				self.pil_cover = PIL.Image.open(file_name)
			except:
				tkinter.messagebox.showerror("Error", "Image " + file_name + " cannot be loaded.")
				self.pil_cover = None
				
			self.refresh_cover(self.canvas_cover.winfo_width(), self.canvas_cover.winfo_height())
			
			
	def timer_action_start(self):
		self.button_timer_action.config(text = "Stop")
		if self.timer_id:
			self.window.after_cancel(self.timer_id)
		self.timer_id = self.window.after(1000, self.update_timer)
		
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
		self.label_timer.config(text = "00:00:00")
		
	def timeStrToSec(self, t):
		v = t.split(":")
		return int(v[0]) * 3600 + int(v[1]) * 60 + int(v[2])
		
	def timeSecToStr(self, t):
		h = ("0" + str(t // 3600))[-2:]
		m = ("0" + str((t % 3600) // 60))[-2:]
		s = ("0" + str(t % 60))[-2:]
		return h + ":" + m + ":" + s
		
	def update_timer(self):
		t = self.timeStrToSec(self.label_timer.cget("text"))
		t += 1
		s = self.timeSecToStr(t)
		self.label_timer.config(text = s)
		self.write_file("text-files/timer.txt", s)
		self.timer_id = self.window.after(1000, self.update_timer)
		
	def refresh_cover(self, canvas_width, canvas_height):
		if not self.pil_cover:
			self.canvas_cover.delete("all")
		else:
			img_width, img_height = self.pil_cover.size
			ratio = img_width / img_height
			if img_height < img_width:
				new_width = canvas_width - 10
				new_height = int(new_width / ratio)
			else:
				new_height = canvas_height - 10
				new_width = int(new_height * ratio)
				
			pil_cover_resized = self.pil_cover.resize((new_width, new_height), PIL.Image.ANTIALIAS)
			self.img_cover = PIL.ImageTk.PhotoImage(pil_cover_resized) # reference to image must be kept to avoid garbage deletion
			self.canvas_cover.create_image((canvas_width // 2, canvas_height // 2), image = self.img_cover)
			
	def get_json(self, url):
		request = urllib.request.Request(url)
		response = urllib.request.urlopen(request).read()
		return json.loads(response.decode('utf-8'))
		
	def get_sheet_values(self, sheet_name, cell_range):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/values/" + sheet_name + "!" + cell_range + "/?key=" + self.config["SHEET"]["API_KEY"];
		data = self.get_json(url)
		
		if "values" not in data:
			return None
		else:
			return data["values"]
		
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
		self.fill_timer()
		
	def fill_consoles(self):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "?key=" + self.config["SHEET"]["API_KEY"]
		
		data = self.get_json(url)
		
		values = []
		
		if data["sheets"]:
			for i in range(int(self.config["SHEET"]["FIRST_GAME_CONSOLE_SHEET"]) - 1, len(data["sheets"])):
				item = data["sheets"][i];
				if item["properties"] and item["properties"]["title"]:
					values.append(item["properties"]["title"])
					
		self.combo_consoles.config(values = values)
		self.combo_consoles.current(0)
		
		self.process_on_combo_consoles_changed()
		
	def fill_games(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		cell_range = self.config["SHEET"]["GAME_NAME_COLUMN"] + self.config["SHEET"]["FIRST_GAME_LINE"] + ":" + self.config["SHEET"]["TIMER_COLUMN"] + "1000"
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
		
	def fill_timer(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		game_id = int(self.config["SHEET"]["FIRST_GAME_LINE"]) + self.combo_games.current()
		cell = self.config["SHEET"]["TIMER_COLUMN"] + str(game_id)
		sheet_values = self.get_sheet_values(console, cell + ":" + cell)
		
		value = "00:00:00"
		
		if sheet_values and sheet_values[0] and sheet_values[0][0]:
			value = sheet_values[0][0]
			
		self.timer_action_stop()
		self.label_timer.config(text = value)
		
	def write_file(self, file_name, value):
		nb_retries = 0
		while nb_retries < 5:
			try:
				with open(file_name, "w") as f:
					f.write(value)
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
	
