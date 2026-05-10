from neko2020.application.ports import ICursorProvider
from neko2020.domain.value_objects import Point


class TkinterCursorProvider(ICursorProvider):
    def __init__(self, root):
        self._root = root

    def get_cursor_position(self) -> Point:
        return Point(
            self._root.winfo_pointerx(),
            self._root.winfo_pointery(),
        )
