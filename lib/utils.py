
import time
import shutil
import traceback


class Utils():
	
	def print_stack(self):
		traceback.print_stack()
		
	def timeStrToSec(self, t):
		if t == "":
			return 0
		
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
		
	def progressValuesToStr(self, value, total):
		return str(value) + "/" + str(total)
		
	def progressStrToValues(self, s):
		values = s.split("/")
		return int(values[0]), int(values[1])
		
	def write_file(self, mode, file_name, value):
		nb_retries = 0
		while nb_retries < 5:
			try:
				with open(file_name, mode, encoding="utf-8") as f:
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
	
	def split_sheet_a1_value(self, a1_value):
		v = a1_value.split("!")
		return v[0], v[1]
		