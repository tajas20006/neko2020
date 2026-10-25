from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class Size:
    cx: int
    cy: int


@dataclass(frozen=True, slots=True)
class Rect:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top
