import os
import time

import ctypes
import tkinter as tk
from infi.systray import SysTrayIcon

from neko2020 import neko
from neko2020.utils import files, configs

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x80

STOP_UPDATE = False


def stop(root):
    global STOP_UPDATE
    STOP_UPDATE = True

    fps = configs.get_int("fps")

    # this is to keep the application running when neko is hidden
    def nop():
        if not STOP_UPDATE:
            return
        root.after(fps, nop)

    nop()


def start(root, canvas):
    global STOP_UPDATE
    STOP_UPDATE = False

    # reload config
    configs.load_config()
    myNeko = neko.Neko(root, canvas)
    fps = configs.get_int("fps")

    def timer(root, myNeko, fps=200):
        if STOP_UPDATE:
            return
        myNeko.update()
        root.after(fps, lambda: timer(root, myNeko, fps))

    timer(root, myNeko, fps)


def restart(root, canvas):
    fps = configs.get_int("fps")
    stop(root)
    # sleep before restarting to let the old instance have time to exit.
    time.sleep(2 * fps / 1000)
    start(root, canvas)


def quit(root):
    root.quit()


def _hide_from_alt_tab(root):
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_TOOLWINDOW
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)


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

    with SysTrayIcon(
        icon=os.path.join(
            files.get_project_root(),
            "resource",
            "neko",
            "Awake.ico",
        ),
        hover_text="neko",
        menu_options=(
            ("Stop", None, lambda _: stop(root)),
            ("Start", None, lambda _: start(root, canvas)),
            ("Restart", None, lambda _: restart(root, canvas)),
        ),
        on_quit=lambda _: quit(root),
    ):
        start(root, canvas)
        root.mainloop()
