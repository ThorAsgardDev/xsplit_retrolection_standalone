
import os
import traceback
import time
import configparser
import urllib
import urllib.request
import requests
import io
import json
import shutil
import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk
import games_db_client


class MainFrame(tkinter.Frame):

	def __init__(self, window, **kwargs):
		tkinter.Frame.__init__(self, window, **kwargs)
		
		self.window = window
		self.pil_cover = None
		self.pil_cover_thumbnail = None
		self.cover_file_name = ""
		self.cover_is_local = True
		self.db_cover_file_name = ""
		self.timer_id = None
		self.timer_total_reset_value = "00:00:00"
		
		self.config = configparser.ConfigParser()
		self.config.read("config.ini")
		
		self.pack(expand = tkinter.YES, fill = tkinter.BOTH)
		
		menu_bar = tkinter.Menu(self.window)
		file_menu = tkinter.Menu(menu_bar, tearoff=0)
		file_menu.add_command(label = "Open", command = self.on_menu_file_open)
		file_menu.add_command(label = "Save", command = self.on_menu_file_save)
		menu_bar.add_cascade(label = "File", menu = file_menu)
		
		self.window.config(menu = menu_bar)
		
		self.frame_left = tkinter.Frame(self, width = 300)
		self.frame_left.pack_propagate(False)
		self.frame_left.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		self.frame_right = tkinter.Frame(self, width = 300)
		self.frame_right.pack_propagate(False)
		self.frame_right.pack(side = tkinter.RIGHT, fill = tkinter.BOTH)
		
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
		
		self.frame_db_console_info = tkinter.LabelFrame(self.frame_right, text = "Informations console")
		self.frame_db_console_info.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		self.frame_db_console_info_labels = tkinter.Frame(self.frame_db_console_info)
		self.frame_db_console_info_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		self.frame_db_console_info_values = tkinter.Frame(self.frame_db_console_info)
		self.frame_db_console_info_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)
		
		self.frame_db_game_info = tkinter.LabelFrame(self.frame_right, text = "Informations jeu")
		self.frame_db_game_info.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
		
		self.frame_db_game_info_top = tkinter.Frame(self.frame_db_game_info)
		self.frame_db_game_info_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
		
		self.frame_db_game_info_top_labels = tkinter.Frame(self.frame_db_game_info_top)
		self.frame_db_game_info_top_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
		
		self.frame_db_game_info_top_values = tkinter.Frame(self.frame_db_game_info_top)
		self.frame_db_game_info_top_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)
		
		self.frame_db_game_info_bottom = tkinter.Frame(self.frame_db_game_info)
		self.frame_db_game_info_bottom.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		self.frame_db_game_info_canvas = tkinter.Frame(self.frame_db_game_info)
		self.frame_db_game_info_canvas.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
		
		pil_img = PIL.Image.open("resources/retrolection.png")
		self.img_logo = PIL.ImageTk.PhotoImage(pil_img) # reference to image must be kept to avoid garbage deletion
		canvas = tkinter.Canvas(self.frame_logo, width = self.img_logo.width(), height = self.img_logo.height())
		canvas.create_image((0, 0), anchor = tkinter.NW, image = self.img_logo)
		canvas.pack(side = tkinter.LEFT)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Consoles: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.combo_consoles = tkinter.ttk.Combobox(self.frame_sheet_values, state = "readonly")
		self.combo_consoles.pack(padx = 5, pady = 5, fill = tkinter.X)
		self.combo_consoles.bind("<<ComboboxSelected>>", self.on_combo_consoles_changed)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Jeux: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.combo_games = tkinter.ttk.Combobox(self.frame_sheet_values, state = "readonly")
		self.combo_games.pack(padx = 5, pady = 5, fill = tkinter.X)
		self.combo_games.bind("<<ComboboxSelected>>", self.on_combo_games_changed)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Progression console: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_progress_console = tkinter.Label(self.frame_sheet_values, anchor = tkinter.W)
		self.label_progress_console.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Progression totale: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_progress_total = tkinter.Label(self.frame_sheet_values, anchor = tkinter.W)
		self.label_progress_total.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Viewer sub: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_viewer_sub = tkinter.Label(self.frame_sheet_values, anchor = tkinter.W)
		self.label_viewer_sub.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Viewer don: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_viewer_don = tkinter.Label(self.frame_sheet_values, anchor = tkinter.W)
		self.label_viewer_don.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Défi sub: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_challenge_sub = tkinter.Label(self.frame_sheet_values, anchor = tkinter.W)
		self.label_challenge_sub.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_sheet_labels, anchor = tkinter.W, text = "Défi don: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_challenge_don = tkinter.Label(self.frame_sheet_values, anchor = tkinter.W)
		self.label_challenge_don.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		button = tkinter.Button(self.frame_sheet_bottom, relief = tkinter.GROOVE, text = "Envoyer les valeurs vers XSplit", command = self.on_update_xsplit_click)
		button.pack(fill = tkinter.X, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_timer_labels, anchor = tkinter.W, text = "Jeu en cours: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_timer_game = tkinter.Label(self.frame_timer_values, anchor = tkinter.W)
		self.label_timer_game.pack(anchor = tkinter.W, padx = 5, pady = 5)
		
		label = tkinter.Label(self.frame_timer_labels, anchor = tkinter.W, text = "Total Retrolection: ")
		label.pack(anchor = tkinter.W, padx = 5, pady = 5)
		self.label_timer_total = tkinter.Label(self.frame_timer_values, anchor = tkinter.W)
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
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Nom: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_name = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_name.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Constructeur: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_manufacturer = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_manufacturer.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Media: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_media = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_media.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "CPU: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_cpu = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_cpu.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Mémoire: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_memory = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_memory.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Graphisme: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_graphics = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_graphics.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Son: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_sound = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_sound.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Port(s) manette: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_max_controllers = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_max_controllers.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Affichage: ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_display = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_display.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Date de sortie (Japon): ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_release_date_japan = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_release_date_japan.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Date de sortie (US): ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_release_date_us = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_release_date_us.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_console_info_labels, anchor = tkinter.W, text = "Date de sortie (EU): ")
		label.pack(anchor = tkinter.W)
		self.label_db_console_release_date_eu = tkinter.Label(self.frame_db_console_info_values, anchor = tkinter.W)
		self.label_db_console_release_date_eu.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_game_info_top_labels, anchor = tkinter.W, text = "Titre trouvés: ")
		label.pack(anchor = tkinter.W)
		self.combo_db_games = tkinter.ttk.Combobox(self.frame_db_game_info_top_values, state = "readonly")
		self.combo_db_games.pack(fill = tkinter.X)
		self.combo_db_games.bind("<<ComboboxSelected>>", self.on_combo_db_games_changed)
		
		label = tkinter.Label(self.frame_db_game_info_top_labels, anchor = tkinter.W, text = "Date de sortie: ")
		label.pack(anchor = tkinter.W)
		self.label_db_game_release_date = tkinter.Label(self.frame_db_game_info_top_values, anchor = tkinter.W)
		self.label_db_game_release_date.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_game_info_top_labels, anchor = tkinter.W, text = "Nombre de joueurs: ")
		label.pack(anchor = tkinter.W)
		self.label_db_game_players = tkinter.Label(self.frame_db_game_info_top_values, anchor = tkinter.W)
		self.label_db_game_players.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_game_info_top_labels, anchor = tkinter.W, text = "Titre(s) alternatif(s): ")
		label.pack(anchor = tkinter.W)
		self.label_db_game_alternates = tkinter.Label(self.frame_db_game_info_top_values, anchor = tkinter.W)
		self.label_db_game_alternates.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_game_info_top_labels, anchor = tkinter.W, text = "Developpeur(s): ")
		label.pack(anchor = tkinter.W)
		self.label_db_game_developers = tkinter.Label(self.frame_db_game_info_top_values, anchor = tkinter.W)
		self.label_db_game_developers.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_game_info_top_labels, anchor = tkinter.W, text = "Editeur(s): ")
		label.pack(anchor = tkinter.W)
		self.label_db_game_publishers = tkinter.Label(self.frame_db_game_info_top_values, anchor = tkinter.W)
		self.label_db_game_publishers.pack(anchor = tkinter.W)
		
		label = tkinter.Label(self.frame_db_game_info_top_labels, anchor = tkinter.W, text = "Jaquette: ")
		label.pack(anchor = tkinter.W)
		
		self.canvas_cover_thumbnail = tkinter.Canvas(self.frame_db_game_info_canvas, bg = "black")
		self.canvas_cover_thumbnail.bind("<Configure>", self.canvas_cover_thumbnail_configure)
		self.canvas_cover_thumbnail.pack(side = tkinter.TOP, padx = 2, pady = 2)
		
		button = tkinter.Button(self.frame_db_game_info_bottom, relief = tkinter.GROOVE, text = "<< Utiliser cette jaquette", command = self.on_use_this_cover_click)
		button.pack(side = tkinter.TOP, fill = tkinter.X, padx = 5, pady = 5)
		
	def on_menu_file_open(self):
		file_name = tkinter.filedialog.askopenfilename(defaultextension = "*.rcx", filetypes = [("Retrolection context files", "*.rcx")])
		if len(file_name) >= 1:
			self.load_context(file_name)
			
	def on_menu_file_save(self):
		file_name = tkinter.filedialog.asksaveasfilename(defaultextension = "*.rcx", filetypes = [("Retrolection context files", "*.rcx")])
		if len(file_name) >= 1:
			self.save_context(file_name)
			
	def canvas_cover_configure(self, event):
		self.refresh_cover(event.width, event.height)
		
	def canvas_cover_thumbnail_configure(self, event):
		self.refresh_cover_thumbnail(event.width, event.height)
		
	def on_update_xsplit_click(self):
		self.write_file("w", "text-files/game.txt", self.combo_games.cget("values")[self.combo_games.current()])
		self.write_file("w", "text-files/progression-console.txt", self.label_progress_console.cget("text"))
		self.write_file("w", "text-files/progression-total.txt", self.label_progress_total.cget("text"))
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
			
	def on_use_this_cover_click(self):
		self.load_cover(self.db_cover_file_name, False)
		
	def on_cover_load_click(self):
		file_name = tkinter.filedialog.askopenfilename()
		self.load_cover(file_name, True)
		
	def load_cover(self, file_name, is_local):
		if file_name:
			self.cover_is_local = is_local
			self.cover_file_name = file_name
			try:
				if is_local:
					self.pil_cover = PIL.Image.open(file_name)
				else:
					response = requests.get(file_name)
					image_data = io.BytesIO(response.content)
					self.pil_cover = PIL.Image.open(image_data)
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
			
	def load_cover_thumbnail(self, file_name):
		if file_name:
			try:
				response = requests.get(file_name)
				image_data = io.BytesIO(response.content)
				self.pil_cover_thumbnail = PIL.Image.open(image_data)
			except Exception as e:
				print("Unexpected error: ", traceback.format_exc())
				self.pil_cover_thumbnail = None
				
			self.refresh_cover_thumbnail(self.canvas_cover_thumbnail.winfo_width(), self.canvas_cover_thumbnail.winfo_height())
			
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
		
		ratio_width = img_width / width
		ratio_height = img_height / height
		
		ratio_img = img_width / img_height
		if ratio_width >= ratio_height:
			new_width = width - 10
			new_height = int(new_width / ratio_img)
		else:
			new_height = height - 10
			new_width = int(new_height * ratio_img)
			
		return image.resize((new_width, new_height), PIL.Image.ANTIALIAS)
		
	def refresh_cover(self, canvas_width, canvas_height):
		if not self.pil_cover:
			self.canvas_cover.delete("all")
		else:
			pil_cover_resized = self.resize_image(self.pil_cover, canvas_width, canvas_height)
			self.img_cover = PIL.ImageTk.PhotoImage(pil_cover_resized) # reference to image must be kept to avoid garbage deletion
			self.canvas_cover.create_image((canvas_width // 2, canvas_height // 2), image = self.img_cover)
			
	def refresh_cover_thumbnail(self, canvas_width, canvas_height):
		if not self.pil_cover_thumbnail:
			self.canvas_cover_thumbnail.delete("all")
		else:
			pil_cover_thumbnail_resized = self.resize_image(self.pil_cover_thumbnail, canvas_width, canvas_height)
			self.img_cover_thumbnail = PIL.ImageTk.PhotoImage(pil_cover_thumbnail_resized) # reference to image must be kept to avoid garbage deletion
			self.canvas_cover_thumbnail.create_image((canvas_width // 2, canvas_height // 2), image = self.img_cover_thumbnail)
			
	def get_json(self, url):
		request = urllib.request.Request(url)
		response = urllib.request.urlopen(request).read()
		return json.loads(response.decode('utf-8'))
		
	def get_sheet_values(self, sheet_name, cell_range):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/values/" + urllib.parse.quote(sheet_name) + "!" + cell_range + "/?key=" + self.config["SHEET"]["GDOC_API_KEY"];
		data = self.get_json(url)
		
		if "values" not in data:
			return None
		else:
			return data["values"]
			
	def get_sheet_properties(self, sheet_name, cell_range):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/?key=" + self.config["SHEET"]["GDOC_API_KEY"] + "&ranges=" + urllib.parse.quote(sheet_name) + "!" + cell_range + "&includeGridData=true";
		data = self.get_json(url)
		
		return data["sheets"][0]["data"][0]["rowData"][0]["values"]
		
	def on_combo_consoles_changed(self, event):
		self.process_on_combo_consoles_changed()
		
	def on_combo_games_changed(self, event):
		self.process_on_combo_games_changed()
		
	def on_combo_db_games_changed(self, event):
		self.process_on_combo_db_games_changed()
		
	def process_on_combo_consoles_changed(self):
		self.fill_games()
		self.fill_progress_console()
		self.fill_db_consoles()
		
	def process_on_combo_games_changed(self):
		self.fill_viewer_sub()
		self.fill_viewer_don()
		self.fill_challenge_sub()
		self.fill_challenge_don()
		self.fill_timers()
		self.fill_db_games()
		
	def process_on_combo_db_games_changed(self):
		self.canvas_cover_thumbnail.delete("all")
		if self.combo_db_games.current() >= 0:
			db_game = self.combo_db_games.cget("values")[self.combo_db_games.current()]
			
			info = self.games_db_client.get_game_info(self.combo_db_games.value_to_id[db_game])
			
			self.label_db_game_release_date.config(text = info["release_date"])
			players_str = str(info["players"]) + " (Co-op: " + info["coop"] + ")"
			self.label_db_game_players.config(text = players_str)
			self.label_db_game_alternates.config(text = info["alternates"])
			self.label_db_game_developers.config(text = info["developers"])
			self.label_db_game_publishers.config(text = info["publishers"])
			
			self.db_cover_file_name = info["url_image"]
			
			self.load_cover_thumbnail(info["url_image_thumbnail"])
			
	def fill_db_consoles(self):
		try:
			console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
			
			info = self.games_db_client.get_platform_info(console)
			
			self.label_db_console_name.config(text = info["name"])
			self.label_db_console_manufacturer.config(text = info["manufacturer"])
			self.label_db_console_media.config(text = info["media"])
			self.label_db_console_cpu.config(text = info["cpu"])
			self.label_db_console_memory.config(text = info["memory"])
			self.label_db_console_graphics.config(text = info["graphics"])
			self.label_db_console_sound.config(text = info["sound"])
			self.label_db_console_max_controllers.config(text = info["max_controllers"])
			self.label_db_console_display.config(text = info["display"])
			self.label_db_console_release_date_japan.config(text = info["release_date_japan"])
			self.label_db_console_release_date_us.config(text = info["release_date_us"])
			self.label_db_console_release_date_eu.config(text = info["release_date_eu"])
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			
	def fill_db_games(self):
		try:
			console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
			game = self.combo_games.cget("values")[self.combo_games.current()]
			
			found_games = self.games_db_client.search_game_by_name(game, console)
			
			value_to_id = {}
			values = []
			
			for v in found_games:
				values.append(v["title"])
				value_to_id[v["title"]] = v["id"]
				
			self.combo_db_games.set("")
			
			self.combo_db_games.value_to_id = value_to_id
			self.combo_db_games.config(values = values)
			
			if len(values) >= 1:
				self.combo_db_games.current(0)
			
			self.process_on_combo_db_games_changed()
		except Exception as e:
			print("Unexpected error: ", traceback.format_exc())
			
	def fill_consoles(self):
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "?key=" + self.config["SHEET"]["GDOC_API_KEY"]
		
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
		
	def fill_games(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		cell_range = self.config["SHEET"]["GAME_NAME_COLUMN"] + self.config["SHEET"]["FIRST_GAME_LINE"] + ":" + self.config["SHEET"]["TIMER_GAME_COLUMN"] + "1000"
		sheet_values = self.get_sheet_values(console, cell_range)
		
		values = []
		
		if sheet_values:
			for v in sheet_values:
				if len(v) >= 1 and v[0] and v[0] != "":
					values.append(v[0])
					
		self.combo_games.config(values = values)
		self.combo_games.current(0)
		
		self.process_on_combo_games_changed()
		
	def fill_progress_console(self):
		console = self.combo_consoles.cget("values")[self.combo_consoles.current()]
		cell_range = self.config["SHEET"]["PROGRESSION_CELL_RANGE"]
		sheet_values = self.get_sheet_values(console, cell_range)
		
		self.label_progress_console.config(text = sheet_values[0][0] + "/" + sheet_values[0][2])
		
	def fill_progress_total(self):
		consoles = self.combo_consoles.cget("values")
		
		ranges = ""
		for c in consoles:
			ranges += "&ranges=" + urllib.parse.quote(c) + "!" + self.config["SHEET"]["PROGRESSION_CELL_RANGE"]
			
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/values:batchGet?key=" + self.config["SHEET"]["GDOC_API_KEY"] + ranges;
		
		data = self.get_json(url)
		
		number_of_games_completed = 0
		number_of_games_total = 0
		for v in data["valueRanges"]:
			number_of_games_completed += int(v["values"][0][0])
			number_of_games_total += int(v["values"][0][2])
			
		self.label_progress_total.config(text = str(number_of_games_completed) + '/' + str(number_of_games_total))
		
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
						if "formattedValue" in p:
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
				
		url = "https://sheets.googleapis.com/v4/spreadsheets/" + self.config["SHEET"]["SPREAD_SHEET_ID"] + "/values:batchGet?key=" + self.config["SHEET"]["GDOC_API_KEY"] + ranges;
		
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
				
	def get_combo_value(self, combo):
		value = ""
		current_index = combo.current()
		values = combo.cget("values")
		if current_index >= 0 and current_index < len(values):
			value = values[current_index]
		return value
		
	def select_combo_value(self, combo, value):
		values = combo.cget("values")
		
		i = 0
		for v in values:
			if v == value:
				combo.current(i)
				return True
			i += 1
			
		return False
		
	def load(self):
		self.games_db_client = games_db_client.GamesDbClient(self.config["DATA_BASES"]["THE_GAMES_DB_API_KEY"], self.config["DATA_BASES"]["IGDB_API_KEY"])
		self.fill_consoles()
		self.fill_progress_total()
		
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
					
					cover_is_local = True
					if "cover_is_local" in config["CONTEXT"]:
						cover_is_local = config["CONTEXT"].getboolean("cover_is_local")
					self.load_cover(config["CONTEXT"]["cover"], cover_is_local)
					
		return ret
		
	def save_context(self, file_name):
		config = configparser.ConfigParser()
		
		config["CONTEXT"] = {
			"console": self.get_combo_value(self.combo_consoles),
			"game": self.get_combo_value(self.combo_games),
			"cover_is_local": self.cover_is_local,
			"cover": self.cover_file_name,
		}
		
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
	
