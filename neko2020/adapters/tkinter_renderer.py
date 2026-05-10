import os
import tkinter as tk

from neko2020.application.ports import IConfigProvider, IRenderer
from neko2020.domain.value_objects import Point, Rect, Size
from neko2020.infrastructure import files, image_loader


class TkinterRenderer(IRenderer):
    def __init__(
        self,
        canvas,
        config: IConfigProvider,
        vx: int,
        vy: int,
        initial_position: Point,
    ):
        self._canvas = canvas
        # vx/vy: virtual-screen origin in screen coords; used to convert
        # screen coordinates to canvas pixel coordinates.
        self._vx = vx
        self._vy = vy
        self._position = initial_position
        self._bounds = Rect(
            vx, vy, vx + canvas.winfo_width(), vy + canvas.winfo_height()
        )

        pet_type = config.get_string("animal")
        user_resource_base = files.get_user_resource_dir()
        if pet_type == "random":
            pet_type = files.select_random_directory_merged(
                os.path.join(files.get_project_root(), "resource"),
                user_resource_base,
            )

        self._images, img_w, img_h = image_loader.load_images(
            pet_type, user_resource_base=user_resource_base
        )
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
        # Convert screen coords to canvas pixel coords.
        self._canvas.create_image(
            x - self._vx,
            y - self._vy,
            image=self._images[int(frame_index)],
            anchor=tk.CENTER,
        )
