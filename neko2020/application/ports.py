from abc import ABC, abstractmethod

from neko2020.domain.state_machine import State
from neko2020.domain.value_objects import Point, Rect, Size


class IConfigProvider(ABC):
    @abstractmethod
    def get_int(self, path: str) -> int: ...

    @abstractmethod
    def get_float(self, path: str) -> float: ...

    @abstractmethod
    def get_string(self, path: str) -> str: ...

    @abstractmethod
    def get_bool(self, path: str) -> bool: ...

    @abstractmethod
    def reload(self) -> None: ...

    @abstractmethod
    def save(self, data: dict) -> None:
        """Persist `data` as the user's settings, replacing the old ones."""


class ICursorProvider(ABC):
    @abstractmethod
    def get_cursor_position(self) -> Point: ...


class IRenderer(ABC):
    @abstractmethod
    def render(self, state: State, phase: int, x: int, y: int) -> None: ...

    @abstractmethod
    def get_position(self) -> Point: ...

    @abstractmethod
    def get_size(self) -> Size: ...

    @abstractmethod
    def get_bounds(self) -> Rect: ...
