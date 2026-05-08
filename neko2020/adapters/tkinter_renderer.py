import os
import tkinter as tk

from neko2020.application.ports import IConfigProvider, IRenderer
from neko2020.domain.value_objects import Point, Rect, Size
from neko2020.infrastructure import files, image_loader


class TkinterRenderer(IRenderer):
    def __init__(self, canvas, config: IConfigProvider):
        self._canvas = canvas
        self._position = Point(0, 0)
        self._bounds = Rect(0, 0, canvas.winfo_width(), canvas.winfo_height())

        pet_type = config.get_string("animal")
        if pet_type == "random":
            pet_type = files.select_random_directory(
                os.path.join(files.get_project_root(), "resource")
            )

        self._images, img_w, img_h = image_loader.load_images(pet_type)
        self._size = Size(img_w, img_h)
        self._last_frame_index: int | None = None

    def get_position(self) -> Point:
        return self._position

    def get_size(self) -> Size:
        return self._size

    def get_bounds(self) -> Rect:
        return self._bounds

    def render(self, frame_index: int, x: int, y: int) -> None:
        new_position = Point(x, y)
        if (
            frame_index == self._last_frame_index
            and new_position == self._position
        ):
            return
        self._canvas.delete("all")
        self._position = new_position
        self._last_frame_index = frame_index
        self._canvas.create_image(
            self._position.x,
            self._position.y,
            image=self._images[int(frame_index)],
            anchor=tk.NW,
        )
