from unittest.mock import MagicMock

from neko2020.adapters.tkinter_cursor import TkinterCursorProvider
from neko2020.domain.value_objects import Point


# ---------------------------------------------------------------------------
# get_cursor_position
# ---------------------------------------------------------------------------


def test_get_cursor_position_returns_point():
    root = MagicMock()
    root.winfo_pointerx.return_value = 100
    root.winfo_pointery.return_value = 200
    provider = TkinterCursorProvider(root)
    result = provider.get_cursor_position()
    assert isinstance(result, Point)


def test_get_cursor_position_xy_match_winfo_values():
    root = MagicMock()
    root.winfo_pointerx.return_value = 100
    root.winfo_pointery.return_value = 200
    provider = TkinterCursorProvider(root)
    result = provider.get_cursor_position()
    assert result.x == 100
    assert result.y == 200


def test_get_cursor_position_calls_winfo_methods_each_invocation():
    root = MagicMock()
    root.winfo_pointerx.return_value = 0
    root.winfo_pointery.return_value = 0
    provider = TkinterCursorProvider(root)
    provider.get_cursor_position()
    provider.get_cursor_position()
    assert root.winfo_pointerx.call_count == 2
    assert root.winfo_pointery.call_count == 2


def test_get_cursor_position_reflects_updated_values():
    root = MagicMock()
    root.winfo_pointerx.side_effect = [10, 50]
    root.winfo_pointery.side_effect = [20, 80]
    provider = TkinterCursorProvider(root)
    first = provider.get_cursor_position()
    second = provider.get_cursor_position()
    assert first == Point(10, 20)
    assert second == Point(50, 80)
