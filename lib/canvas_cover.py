
import tkinter
import io
import PIL.Image
import PIL.ImageTk
import requests
import tkinter.messagebox


class CanvasCover():
	
	def __init__(self, frame):
		self.image_path = None
		self.pil_image = None
		self.image_object = None
		self.canvas = None
		
		self.canvas = tkinter.Canvas(frame, bg = "black")
		self.canvas.pack(expand = tkinter.YES, fill = tkinter.BOTH)
		self.canvas.bind("<Configure>", self.canvas_configure)
		
	def canvas_configure(self, event):
		self.refresh(event.width, event.height)
		
	def refresh(self, width, height):
		if not self.pil_image:
			self.canvas.delete("all")
		else:
			pil_image_resized = self.resize_image(self.pil_image, width, height)
			self.image_object = PIL.ImageTk.PhotoImage(pil_image_resized) # reference to image must be kept to avoid garbage deletion
			self.canvas.create_image((width // 2, height // 2), image = self.image_object)
			
	def has_image(self):
		if not self.pil_image:
			return False
		return True
		
	def get_image_path(self):
		return self.image_path
		
	def load_image(self, image_path, is_local, resized_image_file_name):
		self.image_path = image_path
		self.pil_image = None
		self.image_object = None
		
		if self.image_path:
			try:
				if is_local:
					self.pil_image = PIL.Image.open(self.image_path)
				else:
					response = requests.get(self.image_path)
					image_data = io.BytesIO(response.content)
					self.pil_image = PIL.Image.open(image_data)
			except:
				tkinter.messagebox.showerror("Error", "Image " + self.image_path + " cannot be loaded.")
				self.pil_image = None
				
			if resized_image_file_name and self.pil_image:
				pil_image_resized = self.resize_image(self.pil_image, 400, 400)
				pil_image_resized_width, pil_image_resized_height = pil_image_resized.size
				image = PIL.Image.new('RGB', (400, 400), (0, 0, 0))
				image.paste(pil_image_resized, ((400 - pil_image_resized_width) // 2, (400 - pil_image_resized_height) // 2))
				image.save(resized_image_file_name)
				
		self.refresh(self.canvas.winfo_width(), self.canvas.winfo_height())
		
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
			
		return pil_image.resize((new_width, new_height), PIL.Image.ANTIALIAS)
		
	def download_image(self, file_name):
		if not self.pil_image:
			return False
			
		self.pil_image.save(file_name)
		return True
		