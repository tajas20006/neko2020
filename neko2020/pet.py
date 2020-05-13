import tkinter as tk
from neko2020.utils import images, classes, configs


class Pet:
    def __init__(self, canvas):
        self.canvas = canvas
        self.position = classes.Point(0, 0)
        self.old_position = classes.Point(-1, -1)
        left, up = 0, 0
        right = canvas.winfo_width()
        down = canvas.winfo_height()
        self.bounds = classes.Rect(left, up, right, down)
        self.last_image = None
        self.pet_type = configs.get_string("animal")
        self.images, img_width, img_height = images.load_images(self.pet_type)
        self.size = classes.Size(img_width, img_height)

    def get_position(self):
        return self.position

    def get_size(self):
        return self.size

    def get_bounds_rect(self):
        return self.bounds

    def set_image(self, image):
        if image != self.last_image:
            self.erase()
            self.last_image = image
            self.draw()

    def move_to(self, new_x, new_y):
        if self.old_position.x == -1:
            self.old_position.x = new_x
            self.old_position.y = new_y
        else:
            self.old_position.x = self.position.x
            self.old_position.y = self.position.y

        self.erase()

        self.position.x = new_x
        self.position.y = new_y

        self.draw()

    def set_image_and_move_to(self, image, new_x, new_y):
        self.last_image = image
        self.move_to(new_x, new_y)
        self.draw()

    def draw(self):
        self.canvas.create_image(
            self.position.x,
            self.position.y,
            image=self.images[int(self.last_image)],
            anchor=tk.NW,
        )

    def erase(self):
        self.canvas.delete("all")
