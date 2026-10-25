import ctypes
from types import SimpleNamespace
from unittest.mock import MagicMock

from neko2020.adapters import win32_overlay
from neko2020.domain.value_objects import Rect


def _fake_windll(monkeypatch):
    user32 = MagicMock()
    monkeypatch.setattr(
        ctypes, "windll", SimpleNamespace(user32=user32), raising=False
    )
    return user32


def test_virtual_screen_is_bounding_box_of_monitors():
    monitors = [Rect(-2560, 0, 0, 1440), Rect(0, 100, 1920, 1180)]
    screen = win32_overlay.virtual_screen(monitors)
    assert screen == Rect(-2560, 0, 1920, 1440)
    assert (screen.width, screen.height) == (4480, 1440)


def test_get_monitors_collects_rects_from_enum_callback(monkeypatch):
    user32 = _fake_windll(monkeypatch)
    # WINFUNCTYPE only exists on Windows; pass the callback straight through
    monkeypatch.setattr(
        ctypes, "WINFUNCTYPE", lambda *a: lambda fn: fn, raising=False
    )

    def enum(hdc, clip, proc, data):
        for r in (
            SimpleNamespace(left=0, top=0, right=1920, bottom=1080),
            SimpleNamespace(left=-1280, top=0, right=0, bottom=1024),
        ):
            assert proc(None, None, SimpleNamespace(contents=r), 0) is True

    user32.EnumDisplayMonitors.side_effect = enum
    assert win32_overlay.get_monitors() == [
        Rect(0, 0, 1920, 1080),
        Rect(-1280, 0, 0, 1024),
    ]


def test_hide_from_alt_tab_adds_toolwindow_style(monkeypatch):
    user32 = _fake_windll(monkeypatch)
    user32.GetParent.return_value = 77
    user32.GetWindowLongW.return_value = 0x100
    win32_overlay.hide_from_alt_tab(MagicMock())
    user32.SetWindowLongW.assert_called_once_with(
        77, win32_overlay.GWL_EXSTYLE, 0x100 | win32_overlay.WS_EX_TOOLWINDOW
    )


def test_place_window_uses_set_window_pos_with_negative_origin(monkeypatch):
    user32 = _fake_windll(monkeypatch)
    user32.GetParent.return_value = 77
    win32_overlay.place_window(MagicMock(), Rect(-2560, 0, 1920, 1440))
    user32.SetWindowPos.assert_called_once_with(
        77, None, -2560, 0, 4480, 1440, win32_overlay.SWP_NOZORDER
    )
