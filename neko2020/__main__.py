import ctypes
import ctypes.wintypes
import os
import tkinter as tk

import pystray
from PIL import Image

from neko2020.adapters.tkinter_cursor import TkinterCursorProvider
from neko2020.adapters.tkinter_renderer import TkinterRenderer
from neko2020.adapters.yaml_config import YamlConfigProvider
from neko2020.application.animation_service import AnimationService
from neko2020.application.ports import IConfigProvider
from neko2020.domain.state_machine import NekoStateMachine
from neko2020.domain.value_objects import Point, Rect
from neko2020.infrastructure import files
from neko2020.ui.config_dialog import ConfigDialog

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x80
SWP_NOZORDER = 0x0004


def _get_monitors() -> list[Rect]:
    """Return each physical display's rect in virtual screen coordinates."""
    rects: list[Rect] = []

    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.wintypes.BOOL,
        ctypes.wintypes.HMONITOR,
        ctypes.wintypes.HDC,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.wintypes.LPARAM,
    )

    def _cb(hMon, hDC, lpRect, lParam):
        r = lpRect.contents
        rects.append(Rect(r.left, r.top, r.right, r.bottom))
        return True

    ctypes.windll.user32.EnumDisplayMonitors(
        None, None, MonitorEnumProc(_cb), 0
    )
    return rects


def _virtual_screen(monitors: list[Rect]) -> tuple[int, int, int, int]:
    """Return (left, top, width, height) bounding box of all monitors."""
    left = min(m.left for m in monitors)
    top = min(m.top for m in monitors)
    right = max(m.right for m in monitors)
    bottom = max(m.bottom for m in monitors)
    return left, top, right - left, bottom - top


def _hide_from_alt_tab(root):
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_TOOLWINDOW
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)


def _build_state_machine(config: IConfigProvider) -> NekoStateMachine:
    return NekoStateMachine(
        stop_time=config.get_int("duration.stop"),
        wash_time=config.get_int("duration.wash"),
        scratch_time=config.get_int("duration.scratch"),
        yawn_time=config.get_int("duration.yawn"),
        awake_time=config.get_int("duration.awake"),
        claw_time=config.get_int("duration.claw"),
        awake_rand=config.get_int("duration.awake_rand"),
        min_speed=config.get_int("speed.min"),
        max_speed=config.get_int("speed.max"),
        idle_space=config.get_int("idle_space"),
        offset=Point(config.get_int("offset.x"), config.get_int("offset.y")),
    )


if __name__ == "__main__":
    monitors = _get_monitors()
    vx, vy, vw, vh = _virtual_screen(monitors)

    root = tk.Tk()
    canvas = tk.Canvas(bg="green", width=vw, height=vh, highlightthickness=0)
    canvas.place(x=0, y=0)
    root.overrideredirect(True)
    root.geometry(f"{vw}x{vh}")
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", "green")

    root.after(10, _hide_from_alt_tab, root)
    root.update()

    # geometry() can't express negative screen coordinates; use SetWindowPos.
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    ctypes.windll.user32.SetWindowPos(hwnd, None, vx, vy, vw, vh, SWP_NOZORDER)

    project_root = files.get_project_root()
    xdg_config_home = os.getenv(
        "XDG_CONFIG_HOME",
        os.path.join(os.path.expanduser("~"), ".config"),
    )
    user_config_path = os.path.join(xdg_config_home, "neko2020", "config.yml")
    config = YamlConfigProvider(
        default_path=os.path.join(
            project_root, "config", "default_config.yml"
        ),
        user_path=user_config_path,
    )

    cursor_provider = TkinterCursorProvider(root)

    def session_factory():
        # Start the pet at the cursor's current screen position so it
        # appears on whichever monitor the user is already using.
        initial_pos = cursor_provider.get_cursor_position()
        renderer = TkinterRenderer(canvas, config, vx, vy, initial_pos)
        state_machine = _build_state_machine(config)
        return state_machine, renderer

    def scheduler(delay_ms, callback):
        root.after(delay_ms, callback)

    service = AnimationService(
        config=config,
        cursor=cursor_provider,
        session_factory=session_factory,
        scheduler=scheduler,
        monitors=monitors,
    )

    config_dialog = ConfigDialog(
        parent=root,
        config=config,
        user_path=user_config_path,
        service=service,
    )

    def _open_config():
        root.after(0, config_dialog.open)

    icon_path = os.path.join(project_root, "resource", "neko", "Awake.ico")
    tray_icon = pystray.Icon(
        "neko",
        Image.open(icon_path),
        "neko",
        menu=pystray.Menu(
            pystray.MenuItem(
                "Config", lambda i, item: _open_config(), default=True
            ),
            pystray.MenuItem("Stop", lambda i, item: service.stop()),
            pystray.MenuItem("Start", lambda i, item: service.start()),
            pystray.MenuItem("Restart", lambda i, item: service.restart()),
            pystray.MenuItem("Quit", lambda i, item: root.quit()),
        ),
    )
    tray_icon.run_detached()

    service.start()
    root.mainloop()

    tray_icon.stop()
