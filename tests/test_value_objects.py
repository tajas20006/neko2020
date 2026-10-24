import pytest

from neko2020.domain.value_objects import Point, Rect, Size


def test_rect_width():
    assert Rect(10, 20, 110, 220).width == 100


def test_rect_height():
    assert Rect(10, 20, 110, 220).height == 200


def test_rect_zero_dimensions():
    r = Rect(5, 5, 5, 5)
    assert r.width == 0
    assert r.height == 0


def test_rect_is_frozen():
    r = Rect(0, 0, 100, 100)
    with pytest.raises(Exception):
        r.left = 5  # type: ignore[misc]


def test_point_stores_values():
    p = Point(3, 7)
    assert p.x == 3 and p.y == 7


def test_point_is_frozen():
    with pytest.raises(Exception):
        Point(1, 2).x = 9  # type: ignore[misc]


def test_size_stores_values():
    s = Size(48, 32)
    assert s.cx == 48 and s.cy == 32


def test_size_is_frozen():
    with pytest.raises(Exception):
        Size(32, 32).cx = 99  # type: ignore[misc]
