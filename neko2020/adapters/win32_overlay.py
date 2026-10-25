"""Win32 calls behind the transparent, click-through overlay window."""

import ctypes
import ctypes.wintypes

from neko2020.domain.value_objects import Rect

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x80
SWP_NOZORDER = 0x0004


def get_monitors() -> list[Rect]:
    """Return each physical display's rect in virtual screen coordinates."""
    rects: list[Rect] = []

    monitor_enum_proc = ctypes.WINFUNCTYPE(
        ctypes.wintypes.BOOL,
        ctypes.wintypes.HMONITOR,
        ctypes.wintypes.HDC,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.wintypes.LPARAM,
    )

    def collect(monitor, hdc, rect_ptr, lparam):
        r = rect_ptr.contents
        rects.append(Rect(r.left, r.top, r.right, r.bottom))
        return True

    ctypes.windll.user32.EnumDisplayMonitors(
        None, None, monitor_enum_proc(collect), 0
    )
    return rects


def virtual_screen(monitors: list[Rect]) -> Rect:
    """Return the bounding box of all monitors."""
    return Rect(
        min(m.left for m in monitors),
        min(m.top for m in monitors),
        max(m.right for m in monitors),
        max(m.bottom for m in monitors),
    )


def hide_from_alt_tab(root) -> None:
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_TOOLWINDOW
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)


def place_window(root, rect: Rect) -> None:
    """Move/resize `root` to `rect`.

    Tk's geometry() can't express negative screen coordinates, which a
    monitor left of or above the primary one needs.
    """
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    ctypes.windll.user32.SetWindowPos(
        hwnd, None, rect.left, rect.top, rect.width, rect.height, SWP_NOZORDER
    )
