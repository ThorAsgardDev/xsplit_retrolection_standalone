
import os
import sys
import configparser
import tkinter
import tkinter.ttk
import tkinter.filedialog
import PIL.Image
import PIL.ImageTk
import lib.sheets_client
import lib.utils
import lib.canvas_cover
import lib.remote_controller_server
import time
        

class MainFrame(tkinter.Frame):
    RESIZED_COVER_FILE_NAME = "cover.png"
    
    def __init__(self, window, **kwargs):
        tkinter.Frame.__init__(self, window, **kwargs)
        
        self.__window = window
        
        self.__model = None
        
        self.__timer_id = None
        
        self.__config = configparser.ConfigParser()
        self.__config.read("config.ini")
        
        self.__utils = lib.utils.Utils()
        
        self.__remote_controller_server_thread = lib.remote_controller_server.RemoteControllerServerThread(self.__config, self.__on_remote_controller_request)
        self.__remote_controller_server_thread.start()
        
        self.pack(expand = tkinter.YES, fill = tkinter.BOTH)
        
        menu_bar = tkinter.Menu(self.__window)
        file_menu = tkinter.Menu(menu_bar, tearoff = 0)
        file_menu.add_command(label = "Open", command = self.__on_menu_file_open)
        file_menu.add_command(label = "Save", command = self.__on_menu_file_save)
        menu_bar.add_cascade(label = "File", menu = file_menu)
        
        self.__window.config(menu = menu_bar)
        
        frame_left = tkinter.Frame(self, width = 350)
        frame_left.pack_propagate(False)
        frame_left.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
        
        frame_right = tkinter.Frame(self)
        frame_right.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)

        frame_sheet = tkinter.LabelFrame(frame_left, text = "Gdoc")
        frame_sheet.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)

        frame_sheet_top = tkinter.Frame(frame_sheet)
        frame_sheet_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
        
        frame_sheet_bottom = tkinter.Frame(frame_sheet)
        frame_sheet_bottom.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)
        
        frame_sheet_labels = tkinter.Frame(frame_sheet_top)
        frame_sheet_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
        
        frame_sheet_suffixes = tkinter.Frame(frame_sheet_top, width = 80)
        frame_sheet_suffixes.pack_propagate(False)
        frame_sheet_suffixes.pack(side = tkinter.RIGHT, fill = tkinter.BOTH)

        frame_sheet_values = tkinter.Frame(frame_sheet_top)
        frame_sheet_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)

        frame_run = tkinter.LabelFrame(frame_left, text = "Run")
        frame_run.pack(side = tkinter.TOP, fill = tkinter.BOTH, padx = 5, pady = 5)
        
        frame_run_top = tkinter.Frame(frame_run)
        frame_run_top.pack(side = tkinter.TOP, fill = tkinter.BOTH)
        
        frame_run_bottom = tkinter.Frame(frame_run)
        frame_run_bottom.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)

        frame_run_labels = tkinter.Frame(frame_run_top)
        frame_run_labels.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
        
        frame_run_values = tkinter.Frame(frame_run_top)
        frame_run_values.pack(side = tkinter.RIGHT, expand = tkinter.YES, fill = tkinter.BOTH)

        frame_logo = tkinter.Frame(frame_left)
        frame_logo.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH)

        frame_cover = tkinter.LabelFrame(frame_right, text = "Jaquette")
        frame_cover.pack(side = tkinter.TOP, expand = tkinter.YES, fill = tkinter.BOTH, padx = 5, pady = 5)
        
        pil_img = PIL.Image.open("resources/retrolection.png")
        self.img_logo = PIL.ImageTk.PhotoImage(pil_img) # reference to image must be kept to avoid garbage deletion
        canvas = tkinter.Canvas(frame_logo, width = self.img_logo.width(), height = self.img_logo.height())
        canvas.create_image((0, 0), anchor = tkinter.NW, image = self.img_logo)
        canvas.pack(side = tkinter.LEFT)
        
        self.__combo_consoles, self.__entry_support_suffix = self.__create_combo_with_suffix(frame_sheet_labels, frame_sheet_values, frame_sheet_suffixes, True, "Supports: ", self.__on_combo_consoles_changed)
        self.__combo_games, self.__entry_game_suffix = self.__create_combo_with_suffix(frame_sheet_labels, frame_sheet_values, frame_sheet_suffixes, True, "Jeux: ", self.__on_combo_games_changed)
        self.__label_progression_console, _ = self.__create_label_with_suffix(frame_sheet_labels, frame_sheet_values, frame_sheet_suffixes, False, "Progression console: ")
        self.__label_progression_total, _ = self.__create_label_with_suffix(frame_sheet_labels, frame_sheet_values, frame_sheet_suffixes, False, "Progression totale: ")
        self.__create_button(frame_sheet_bottom, "Recharger Gdoc", self.__on_reload_sheet_click)
        self.__create_button(frame_sheet_bottom, "Envoyer vers OBS", self.__on_send_to_obs_click)

        self.__label_status = self.__create_label(frame_run_labels, frame_run_values, "Statut: ")
        self.__label_version_game = self.__create_label(frame_run_labels, frame_run_values, "Version: ")
        self.__label_estimated_time_game = self.__create_label(frame_run_labels, frame_run_values, "Estimate: ")
        self.__label_timer_game = self.__create_label(frame_run_labels, frame_run_values, "Temps: ")
        self.__label_timer_support = self.__create_label(frame_run_labels, frame_run_values, "Temps support: ")
        self.__label_timer_total = self.__create_label(frame_run_labels, frame_run_values, "Total Retrolection: ")
        self.__button_start_pause = self.__create_button(frame_run_bottom, "Démarrer", self.__on_start_pause_click)
        self.__create_button(frame_run_bottom, "Remettre à zéro", self.__on_reset_click)
        self.__create_button(frame_run_bottom, "Valider", self.__on_validate_click)

        self.__create_button(frame_cover, "Charger...", self.__on_cover_load_click)

        self.__canvas_cover = lib.canvas_cover.CanvasCover(frame_cover)
        
    def __create_combo(self, frame_label, frame_value, text, on_changed_cb):
        label = tkinter.Label(frame_label, anchor = tkinter.W, text = text)
        label.pack(anchor = tkinter.W, padx = 2, pady = 2)
        combo = tkinter.ttk.Combobox(frame_value, state = "readonly")
        combo.pack(padx = 2, pady = 2, fill = tkinter.X)
        combo.bind("<<ComboboxSelected>>", on_changed_cb)

        return combo
    
    def __create_combo_with_suffix(self, frame_label, frame_value, frame_suffix, editable_suffix, text, on_changed_cb):
        combo = self.__create_combo(frame_label, frame_value, text, on_changed_cb)

        suffix_entry = None
        if editable_suffix:
            suffix_entry = tkinter.Entry(frame_suffix)
            suffix_entry.pack(fill = tkinter.X, padx = 2, pady = 3)
        else:
            label = tkinter.Label(frame_suffix, anchor = tkinter.W)
            label.pack(anchor = tkinter.W, padx = 2, pady = 2)

        return combo, suffix_entry
        
    def __create_label(self, frame_label, frame_value, text):
        label = tkinter.Label(frame_label, anchor = tkinter.W, text = text)
        label.pack(anchor = tkinter.W, padx = 2, pady = 2)
        label_value = tkinter.Label(frame_value, anchor = tkinter.W)
        label_value.pack(anchor = tkinter.W, padx = 2, pady = 2)

        return label_value
    
    def __create_label_with_suffix(self, frame_label, frame_value, frame_suffix, editable_suffix, text):
        label_value = self.__create_label(frame_label, frame_value, text)

        suffix_entry = None
        if editable_suffix:
            suffix_entry = tkinter.Entry(frame_suffix)
            suffix_entry.pack(fill = tkinter.X, padx = 2, pady = 3)
        else:
            label = tkinter.Label(frame_suffix, anchor = tkinter.W)
            label.pack(anchor = tkinter.W, padx = 2, pady = 2)

        return label_value, suffix_entry
        
    def __create_button(self, frame, text, on_click_cb):
        button = tkinter.Button(frame, relief = tkinter.GROOVE, text = text, command = on_click_cb)
        button.pack(fill = tkinter.X, padx = 2, pady = 2)
        return button
        
    def __get_combo_value(self, combo):
        current_index = combo.current()
        values = combo.cget("values")
        if current_index >= 0 and current_index < len(values):
            return values[current_index]
        return ""
        
    def __select_combo_value(self, combo, value):
        values = combo.cget("values")
        
        i = 0
        for v in values:
            if v == value:
                combo.current(i)
                return True
            i += 1
            
        return False
        
    def __on_remote_controller_request(self, path):
        if path == "/start_pause":
            self.__on_start_pause_click()
        elif path == "/validate":
            self.__on_validate_click()
        
    def __on_menu_file_open(self):
        file_name = tkinter.filedialog.askopenfilename(defaultextension = "*.rcx", filetypes = [("Retrolection context files", "*.rcx")])
        if len(file_name) >= 1:
            self.__load_context(file_name)
            
    def __on_menu_file_save(self):
        file_name = tkinter.filedialog.asksaveasfilename(defaultextension = "*.rcx", filetypes = [("Retrolection context files", "*.rcx")])
        if len(file_name) >= 1:
            self.__save_context(file_name)
            
    def __on_cover_load_click(self):
        file_name = tkinter.filedialog.askopenfilename()
        self.__canvas_cover.load_image(file_name, None, True, MainFrame.RESIZED_COVER_FILE_NAME)
        self.__on_send_to_obs_click()
        
    def __set_game_model_value(self, value_label, value):
        model_games = self.__model["consoles"][self.__model["current_console"]]["games"]
        model_games[self.__model["current_game_index"]][value_label] = value
        
    def __set_time(self, time_str):
        self.__set_game_model_value("timer", time_str)
        self.__label_timer_game.config(text = time_str)
        self.__utils.write_file("w", "text-files/timer-game.txt", time_str)
        
    def __set_time_support(self, time_str):
        self.__model["consoles"][self.__model["current_console"]]["timer_total"] = time_str
        self.__label_timer_support.config(text = time_str)
        self.__utils.write_file("w", "text-files/timer-support.txt", time_str)
        
    def __set_total_time(self, time_str):
        self.__model["timer_total"] = time_str
        self.__label_timer_total.config(text = time_str)
        self.__utils.write_file("w", "text-files/timer-total.txt", time_str)
        
    def __set_progression_total(self, value):
        self.__model["progression_total"] = value
        self.__label_progression_total.config(text = value)
        self.__utils.write_file("w", "text-files/progression-total.txt", value)
            
    def __set_progression(self, value):
        self.__model["consoles"][self.__model["current_console"]]["progression"] = value
        self.__label_progression_console.config(text = value)
        self.__utils.write_file("w", "text-files/progression-console.txt", value)
        
    def __start_timer(self):
        if self.__timer_id:
            self.__window.after_cancel(self.__timer_id)
        self.__timer_id = self.__window.after(1000, self.__update_timer)
        
    def __stop_timer(self):
        if self.__timer_id:
            self.__window.after_cancel(self.__timer_id)
            self.__timer_id = None
            return True
            
        return False
        
    def __on_reload_sheet_click(self):
        self.__pause_run(True)
        self.__reload_sheet()
        
    def __on_send_to_obs_click(self):
        self.__utils.write_file("w", "text-files/support.txt", self.__combo_consoles.cget("values")[self.__combo_consoles.current()] + self.__entry_support_suffix.get())
        self.__utils.write_file("w", "text-files/game.txt", self.__combo_games.cget("values")[self.__combo_games.current()] + self.__entry_game_suffix.get())
        self.__utils.write_file("w", "text-files/progression-console.txt", self.__label_progression_console.cget("text"))
        self.__utils.write_file("w", "text-files/progression-total.txt", self.__label_progression_total.cget("text"))
        self.__utils.write_file("w", "text-files/version.txt", self.__label_version_game.cget("text"))
        self.__utils.write_file("w", "text-files/estimate.txt", self.__label_estimated_time_game.cget("text"))
        self.__utils.write_file("w", "text-files/timer-game.txt", self.__label_timer_game.cget("text"))
        self.__utils.write_file("w", "text-files/timer-support.txt", self.__label_timer_support.cget("text"))
        self.__utils.write_file("w", "text-files/timer-total.txt", self.__label_timer_total.cget("text"))
        
        if not self.__canvas_cover.has_image():
            self.__utils.copy_file("default-cover.png", "img-files/cover.png")
        else:
            self.__utils.copy_file(MainFrame.RESIZED_COVER_FILE_NAME, "img-files/cover.png")
            
    def __start_run(self):
        self.__button_start_pause.config(text = "Pause")
        self.__start_timer()
        
    def __pause_run(self, save_game_to_sheet):
        self.__button_start_pause.config(text = "Démarrer")
        # If run in progress
        if self.__stop_timer() and save_game_to_sheet:
            self.__save_game_to_sheet()
            
    def __on_start_pause_click(self):
        if self.__button_start_pause.cget("text") == "Démarrer":
            self.__start_run()
        else:
            self.__pause_run(True)
        
    def __on_reset_click(self):
        self.__pause_run(False)
        
        model_console = self.__model["consoles"][self.__model["current_console"]]
        model_game = model_console["games"][self.__model["current_game_index"]]
        
        timer_total_reset_value = self.__utils.timeSecToStr(self.__utils.timeStrToSec(self.__model["timer_total"]) - self.__utils.timeStrToSec(model_game["timer"]))
        self.__set_total_time(timer_total_reset_value)
        timer_support_reset_value = self.__utils.timeSecToStr(self.__utils.timeStrToSec(model_console["timer_total"]) - self.__utils.timeStrToSec(model_game["timer"]))
        self.__set_time_support(timer_support_reset_value)
        self.__set_time("00:00:00")
        
        if model_game["validation_id"] != "":
            value, total = self.__utils.progressStrToValues(self.__model["progression_total"])
            self.__set_progression_total(self.__utils.progressValuesToStr(value - 1, total))
            
            value, total = self.__utils.progressStrToValues(model_console["progression"])
            self.__set_progression(self.__utils.progressValuesToStr(value - 1, total))
            
            model_game["validation_id"] = ""
            
        self.__update_status()
        self.__save_game_to_sheet()
        
    def __on_validate_click(self):
        self.__pause_run(False)
        
        model_console = self.__model["consoles"][self.__model["current_console"]]
        model_game = model_console["games"][self.__model["current_game_index"]]
        if model_game["validation_id"] == "":
            value, total = self.__utils.progressStrToValues(self.__model["progression_total"])
            self.__set_progression_total(self.__utils.progressValuesToStr(value + 1, total))
            
            value, total = self.__utils.progressStrToValues(model_console["progression"])
            self.__set_progression(self.__utils.progressValuesToStr(value + 1, total))
            
            model_game["validation_id"] = str(value + 1)
            
            self.__update_status()
            
        self.__save_game_to_sheet()
        
    def __save_game_to_sheet(self):
        console = self.__model["current_console"]
        model_games = self.__model["consoles"][console]["games"]
        current_game_index = self.__model["current_game_index"]
        
        config_sheet = self.__config["SHEET"]
        sheet_name = console
        line = str(int(config_sheet["FIRST_GAME_LINE"]) + current_game_index)
        ranges_values = [
            {
                "range": sheet_name + "!" + config_sheet["VALIDATION_COLUMN"] + line + ":" + config_sheet["VALIDATION_COLUMN"] + line,
                "values": [[model_games[current_game_index]["validation_id"]]]
            },
            {
                "range": sheet_name + "!" + config_sheet["TIMER_GAME_COLUMN"] + line + ":" + config_sheet["TIMER_GAME_COLUMN"] + line,
                "values": [[model_games[current_game_index]["timer"]]]
            },
        ]
        
        self.sheets_client.set_values(ranges_values)
        
    def __update_timer(self):
        t = self.__utils.timeStrToSec(self.__label_timer_game.cget("text"))
        t += 1
        self.__set_time(self.__utils.timeSecToStr(t))
        
        t = self.__utils.timeStrToSec(self.__label_timer_support.cget("text"))
        t += 1
        self.__set_time_support(self.__utils.timeSecToStr(t))
        
        t = self.__utils.timeStrToSec(self.__label_timer_total.cget("text"))
        t += 1
        self.__set_total_time(self.__utils.timeSecToStr(t))
        
        self.__update_status()
        
        self.__timer_id = self.__window.after(1000, self.__update_timer)
        
    def __on_combo_consoles_changed(self, event):
        self.__process_on_combo_consoles_changed(None)
        
    def __fill_consoles(self, init_values):
        values = []
        
        for value in self.__model["consoles"]:
            values.append(value)
            
        self.__combo_consoles.config(values = values)
        self.__combo_consoles.current(0)
        
        if init_values and ("console" in init_values):
            self.__select_combo_value(self.__combo_consoles, init_values["console"])
            
        self.__process_on_combo_consoles_changed(init_values)
        
    def __process_on_combo_consoles_changed(self, init_values):
        current_console = self.__get_combo_value(self.__combo_consoles)
        if current_console != self.__model["current_console"]:
            self.__model["current_console"] = current_console
            self.__fill_games(init_values)
            self.__label_progression_console.config(text = self.__model["consoles"][current_console]["progression"])
            self.__label_timer_support.config(text = self.__model["consoles"][current_console]["timer_total"])
            
    def __on_combo_games_changed(self, event):
        self.__process_on_combo_games_changed()
        
    def __fill_games(self, init_values):
        values = []
        
        for value in self.__model["consoles"][self.__model["current_console"]]["games"]:
            values.append(value["name"])
            
        self.__combo_games.config(values = values)
        self.__combo_games.current(0)
        
        if init_values and ("game" in init_values):
            self.__select_combo_value(self.__combo_games, init_values["game"])
            
        self.__process_on_combo_games_changed()
        
    def __process_on_combo_games_changed(self):
        current_game = self.__get_combo_value(self.__combo_games)
        
        if current_game != self.__model["current_game"]:
            self.__pause_run(True)
            
            self.__model["current_game"] = current_game
            current_game_index = self.__combo_games.current()
            self.__model["current_game_index"] = current_game_index
            model_games = self.__model["consoles"][self.__model["current_console"]]["games"]
            
            self.__label_version_game.config(text = model_games[current_game_index]["version"])
            self.__label_estimated_time_game.config(text = model_games[current_game_index]["estimated_time"])
            self.__label_timer_game.config(text = model_games[current_game_index]["timer"])
            
            self.__update_status()
            
            self.__on_send_to_obs_click()
            
    def __update_status(self):
        model_game = self.__model["consoles"][self.__model["current_console"]]["games"][self.__model["current_game_index"]]
        if model_game["validation_id"] != "":
            text = "Fait"
        elif model_game["timer"] != "" and model_game["timer"] != "00:00:00":
            text = "En cours"
        else:
            text = "A faire"
            
        self.__label_status.config(text = text)
        
    def __fill_model_from_values(self, values, model_games, field_name):
        id = 0
        for value in values:
            v = value[0] if len(value) > 0 else ""
            model_games[id][field_name] = v
            id += 1
    
    def __build_range(self, config_sheet, key, first_line):
        return config_sheet[key] + first_line + ":" + config_sheet[key]
    
    def __range_equals(self, r, config_sheet, key, first_line):
        return r.startswith(self.__build_range(config_sheet, key, first_line))
        
    def __build_model(self):
        model = {
            "timer_total": "00:00:00",
            "progression_total": "",
            "consoles": {},
            "current_console": "",
            "current_game": "",
            "current_game_index": -1,
        }
        
        config_sheet = self.__config["SHEET"]
        
        response = self.sheets_client.get_sheets()
        
        start_index = int(config_sheet["FIRST_GAME_CONSOLE_SHEET"]) - 1
        for i in range(start_index, start_index + int(config_sheet["NUMBER_OF_GAME_CONSOLE_SHEETS"])):
            model["consoles"][response[i].title] = {
                "games": [],
                "progression": "",
                "timer_total": "00:00:00",
            }
                    
        first_line = config_sheet["FIRST_GAME_LINE"]
        
        ranges = []
        
        for console in model["consoles"]:
            ranges.append(console + "!" + self.__build_range(config_sheet, "VALIDATION_COLUMN", first_line))
            ranges.append(console + "!" + self.__build_range(config_sheet, "GAME_NAME_COLUMN", first_line))
            ranges.append(console + "!" + self.__build_range(config_sheet, "VERSION_GAME_COLUMN", first_line))
            ranges.append(console + "!" + self.__build_range(config_sheet, "ESTIMATED_TIME_NAME_COLUMN", first_line))
            ranges.append(console + "!" + self.__build_range(config_sheet, "TIMER_GAME_COLUMN", first_line))
            ranges.append(console + "!" + config_sheet["PROGRESSION_CELL_RANGE"])
            ranges.append(console + "!" + config_sheet["TIMER_TOTAL_CELL"])
            
        values = self.sheets_client.get_values(ranges)

        nb_games_completed = 0
        nb_games_total = 0

        if "valueRanges" in values:
            for value_range in values["valueRanges"]:
                if "range" in value_range and "values" in value_range:
                    console, r = self.__utils.split_sheet_a1_value(value_range["range"])
                    console = console.strip("'")
                    if self.__range_equals(r, config_sheet, "GAME_NAME_COLUMN", first_line):
                        for value in value_range["values"]:
                            game_name = value[0] if len(value) > 0 else ""
                            model["consoles"][console]["games"].append({
                                "name": game_name,
                                "validation_id": "",
                                "version": "",
                                "estimated_time": "",
                                "timer": "00:00:00",
                            })

            for value_range in values["valueRanges"]:
                if "range" in value_range and "values" in value_range:
                    console, r = self.__utils.split_sheet_a1_value(value_range["range"])
                    console = console.strip("'")
                    if self.__range_equals(r, config_sheet, "VALIDATION_COLUMN", first_line):
                        self.__fill_model_from_values(value_range["values"], model["consoles"][console]["games"], "validation_id")
                    elif self.__range_equals(r, config_sheet, "VERSION_GAME_COLUMN", first_line):
                        self.__fill_model_from_values(value_range["values"], model["consoles"][console]["games"], "version")
                    elif self.__range_equals(r, config_sheet, "ESTIMATED_TIME_NAME_COLUMN", first_line):
                        self.__fill_model_from_values(value_range["values"], model["consoles"][console]["games"], "estimated_time")
                    elif self.__range_equals(r, config_sheet, "TIMER_GAME_COLUMN", first_line):
                        self.__fill_model_from_values(value_range["values"], model["consoles"][console]["games"], "timer")
                    elif r == config_sheet["TIMER_TOTAL_CELL"]:
                        model["consoles"][console]["timer_total"] = value_range["values"][0][0]
                    elif r == config_sheet["PROGRESSION_CELL_RANGE"]:
                        nb_completed = 0
                        nb_total = 0
                        if len(value_range["values"][0]) == 3:
                            nb_completed = int(value_range["values"][0][0])
                            nb_total = int(value_range["values"][0][2])
                            model["consoles"][console]["progression"] = self.__utils.progressValuesToStr(nb_completed, nb_total)

                        nb_games_completed += nb_completed
                        nb_games_total += nb_total
          
        t = 0
        for console in model["consoles"]:
            t += self.__utils.timeStrToSec(model["consoles"][console]["timer_total"])
            
        model["timer_total"] = self.__utils.timeSecToStr(t)
        
        model["progression_total"] = self.__utils.progressValuesToStr(nb_games_completed, nb_games_total)
            
        return model
        
    def load(self):
        st = time.time()
        self.sheets_client = lib.sheets_client.SheetsClient(self.__config["SHEET"]["SPREAD_SHEET_ID"])
        print(time.time(), "load sheets_client init (ms): ", (time.time() - st) * 1000)
        
        st = time.time()
        self.__model = self.__build_model()
        print(time.time(), "load build_model (ms): ", (time.time() - st) * 1000)
        
        self.__label_timer_total.config(text = self.__model["timer_total"])
        self.__label_progression_total.config(text = self.__model["progression_total"])
        
        st = time.time()
        init_values = self.__load_context("context.sav")
        print(time.time(), "load load_context (ms): ", (time.time() - st) * 1000)
        
        self.__fill_consoles(init_values)
        st = time.time()
        print(time.time(), "load fill_consoles (ms): ", (time.time() - st) * 1000)
        
    def __reload_sheet(self):
        init_values = {}
        init_values["console"] = self.__model["current_console"]
        init_values["game"] = self.__model["current_game"]
        
        self.__model = self.__build_model()
        self.__label_timer_total.config(text = self.__model["timer_total"])
        self.__label_progression_total.config(text = self.__model["progression_total"])
        self.__fill_consoles(init_values)
        
    def __load_context(self, file_name):
        init_values = {}
        if os.path.exists(file_name):
            config = configparser.ConfigParser()
            config.read(file_name, encoding="utf-8")
            
            if "console" in config["CONTEXT"]:
                init_values["console"] = config["CONTEXT"]["console"].replace("<SPACE>", " ")
                
            if "game" in config["CONTEXT"]:
                init_values["game"] = config["CONTEXT"]["game"].replace("<SPACE>", " ")
                
            if "cover" in config["CONTEXT"]:
                self.__canvas_cover.load_image(config["CONTEXT"]["cover"], None, True, MainFrame.RESIZED_COVER_FILE_NAME)
                
            if "support_suffix" in config["CONTEXT"]:
                self.__entry_support_suffix.delete(0, tkinter.END)
                self.__entry_support_suffix.insert(0, config["CONTEXT"]["support_suffix"].replace("<SPACE>", " "))
                
            if "game_suffix" in config["CONTEXT"]:
                self.__entry_game_suffix.delete(0, tkinter.END)
                self.__entry_game_suffix.insert(0, config["CONTEXT"]["game_suffix"].replace("<SPACE>", " "))
                
        return init_values
        
    def __save_context(self, file_name):
        config = configparser.ConfigParser()
        
        config["CONTEXT"] = {
            "console": self.__model["current_console"].replace(" ", "<SPACE>"),
            "game": self.__model["current_game"].replace(" ", "<SPACE>"),
            "support_suffix": self.__entry_support_suffix.get().replace(" ", "<SPACE>"),
            "game_suffix": self.__entry_game_suffix.get().replace(" ", "<SPACE>"),
        }
        
        image_path = self.__canvas_cover.get_image_path()
        if image_path:
            config["CONTEXT"]["cover"] = image_path

        with open(file_name, "w", encoding="utf-8") as f:
            config.write(f)
        
    def on_close(self):
        self.__save_context("context.sav")
        try:
            self.__window.destroy()
        except:
            pass
            
def main():
    window = tkinter.Tk()
    window.title("Retrolection")
    window.geometry("1050x650")
    window.geometry(("+" + str(int((window.winfo_screenwidth() - 1050) / 2)) + "+"+ str(int((window.winfo_screenheight() - (650 + 50)) / 2))))
    f = MainFrame(window)
    window.protocol("WM_DELETE_WINDOW", f.on_close)
    icon = tkinter.PhotoImage(file = "resources/icon.png")
    window.tk.call("wm", "iconphoto", window._w, icon)
    window.after(1, f.load)
    window.mainloop()
    

class Logger(object):
    def __init__(self, filename = "logs.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "w")
        
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()
        
if __name__ == "__main__":
    logger = Logger()
    sys.stdout = logger
    sys.stderr = logger
    main()
    