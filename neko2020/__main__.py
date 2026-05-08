import os
import time

import ctypes
import tkinter as tk
import pystray
from PIL import Image

from neko2020 import neko
from neko2020.utils import files, configs

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x80

STOP_UPDATE = True


def stop(root):
    global STOP_UPDATE
    if STOP_UPDATE:
        # already stopped
        return
    STOP_UPDATE = True

    delay_ms = 1000 // configs.get_int("fps")

    # this is to keep the application running when neko is hidden
    def nop():
        if not STOP_UPDATE:
            return
        root.after(delay_ms, nop)

    nop()


def start(root, canvas):
    global STOP_UPDATE
    if not STOP_UPDATE:
        # already running
        return
    STOP_UPDATE = False

    # reload config
    configs.load_config()
    myNeko = neko.Neko(root, canvas)
    delay_ms = 1000 // configs.get_int("fps")

    def timer(root, myNeko, delay_ms=125):
        if STOP_UPDATE:
            return
        myNeko.update()
        root.after(delay_ms, lambda: timer(root, myNeko, delay_ms))

    timer(root, myNeko, delay_ms)


def restart(root, canvas):
    delay_ms = 1000 // configs.get_int("fps")
    stop(root)
    # sleep before restarting to let the old instance have time to exit.
    time.sleep(2 * delay_ms / 1000)
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

    icon_path = os.path.join(
        files.get_project_root(), "resource", "neko", "Awake.ico"
    )
    tray_icon = pystray.Icon(
        "neko",
        Image.open(icon_path),
        "neko",
        menu=pystray.Menu(
            pystray.MenuItem("Stop", lambda i, item: stop(root)),
            pystray.MenuItem("Start", lambda i, item: start(root, canvas)),
            pystray.MenuItem("Restart", lambda i, item: restart(root, canvas)),
            pystray.MenuItem("Quit", lambda i, item: quit(root)),
        ),
    )
    tray_icon.run_detached()

    start(root, canvas)
    root.mainloop()

    tray_icon.stop()
