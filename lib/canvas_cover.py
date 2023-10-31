
import tkinter
import io
import PIL.Image
import PIL.ImageTk
import requests
import tkinter.messagebox
import time


class CanvasCover():
	
	def __init__(self, frame):
		self.image_original_path = None
		self.image_thumb_path = None
		self.is_local = None
		self.pil_image_display = None
		self.pil_image_download = None
		self.image_object = None
		self.canvas = None
		
		self.canvas = tkinter.Canvas(frame, bg = "black")
		self.canvas.pack(expand = tkinter.YES, fill = tkinter.BOTH)
		self.canvas.bind("<Configure>", self.canvas_configure)
		
	def canvas_configure(self, event):
		self.refresh(event.width, event.height)
		
	def refresh(self, width, height):
		if not self.pil_image_display:
			self.canvas.delete("all")
		else:
			pil_image_resized = self.resize_image(self.pil_image_display, width, height)
			if pil_image_resized:
				self.image_object = PIL.ImageTk.PhotoImage(pil_image_resized) # reference to image must be kept to avoid garbage deletion
				self.canvas.create_image((width // 2, height // 2), image = self.image_object)
				
	def has_image(self):
		if not self.pil_image_display:
			return False
		return True
		
	def get_image_path(self):
		return self.image_original_path
		
	def create_pil_image(self, image_path, is_local):
		try:
			if is_local:
				return PIL.Image.open(image_path)
			else:
				response = requests.get(image_path)
				image_data = io.BytesIO(response.content)
				return PIL.Image.open(image_data)
		except:
			tkinter.messagebox.showerror("Error", "Image " + image_path + " cannot be loaded.")
			return None
			
	def load_image(self, image_original_path, image_thumb_path, is_local, resized_image_file_name):
		st = time.time()
		self.image_original_path = image_original_path
		self.image_thumb_path = image_thumb_path
		self.is_local = is_local
		self.pil_image_display = None
		self.pil_image_download = None
		self.image_object = None
		
		if image_thumb_path:
			image_path = image_thumb_path
		elif image_original_path:
			image_path = image_original_path
		else:
			image_path = None
		
		if image_path:
			self.pil_image_display = self.create_pil_image(image_path, is_local)
			
			if not self.image_thumb_path:
				self.pil_image_download = self.pil_image_display
				
			if resized_image_file_name and self.pil_image_display:
				pil_image_resized = self.resize_image(self.pil_image_display, 400, 400)
				if pil_image_resized:
					pil_image_resized_width, pil_image_resized_height = pil_image_resized.size
					image = PIL.Image.new('RGB', (400, 400), (0, 0, 0))
					image.paste(pil_image_resized, ((400 - pil_image_resized_width) // 2, (400 - pil_image_resized_height) // 2))
					image.save(resized_image_file_name)
					
		print(time.time(), "load_image (ms): ", (time.time() - st) * 1000)
		st = time.time()
		self.refresh(self.canvas.winfo_width(), self.canvas.winfo_height())
		print(time.time(), "refresh canvas (ms): ", (time.time() - st) * 1000)
		
	def resize_image(self, pil_image, width, height):
		img_width, img_height = pil_image.size
		
		ratio_width = img_width / width
		ratio_height = img_height / height
		
		ratio_img = img_width / img_height
		if ratio_width >= ratio_height:
			new_width = width - 10
			new_height = int(new_width / ratio_img)
		else:
			new_height = height - 10
			new_width = int(new_height * ratio_img)
			
		if new_width < 0 or new_height < 0:
			return None
		return pil_image.resize((new_width, new_height), PIL.Image.LANCZOS)
		
	def download_image(self, file_name):
		if not self.pil_image_display:
			return False
			
		if not self.pil_image_download:
			self.pil_image_download = self.create_pil_image(self.image_original_path, self.is_local)
			
		if self.pil_image_download:
			self.pil_image_download.save(file_name)
			
		return True
		