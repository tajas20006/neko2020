import ctypes
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
from neko2020.domain.value_objects import Point
from neko2020.infrastructure import files

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x80


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
    root = tk.Tk()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    canvas = tk.Canvas(bg="green", width=w, height=h, highlightthickness=0)
    canvas.place(x=0, y=0)
    root.overrideredirect(True)
    root.geometry(f"{w}x{h}+0+0")
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", "green")

    root.after(10, _hide_from_alt_tab, root)

    root.update()

    project_root = files.get_project_root()
    xdg_config_home = os.getenv(
        "XDG_CONFIG_HOME",
        os.path.join(os.path.expanduser("~"), ".config"),
    )
    config = YamlConfigProvider(
        default_path=os.path.join(
            project_root, "config", "default_config.yml"
        ),
        user_path=os.path.join(xdg_config_home, "neko2020", "config.yml"),
    )

    cursor_provider = TkinterCursorProvider(root)

    def session_factory():
        renderer = TkinterRenderer(canvas, config)
        state_machine = _build_state_machine(config)
        return state_machine, renderer

    def scheduler(delay_ms, callback):
        root.after(delay_ms, callback)

    service = AnimationService(
        config=config,
        cursor=cursor_provider,
        session_factory=session_factory,
        scheduler=scheduler,
    )

    icon_path = os.path.join(project_root, "resource", "neko", "Awake.ico")
    tray_icon = pystray.Icon(
        "neko",
        Image.open(icon_path),
        "neko",
        menu=pystray.Menu(
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
