import os
import tkinter as tk
from infi.systray import SysTrayIcon
from neko2020 import neko
from neko2020.utils import files, configs


def timer(root, myNeko, fps=200):
    myNeko.update()
    root.after(fps, lambda: timer(root, myNeko, fps))


def quit(systray, root):
    root.quit()


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

    root.update()

    myNeko = neko.Neko(root, canvas)
    fps = configs.get_int("fps")

    animal = configs.get_string("animal")
    if animal == "random":
        animal = "neko"
    with SysTrayIcon(
        os.path.join(
            files.get_project_root(), "resource", animal, "Awake.ico",
        ),
        animal,
        set(),
        on_quit=lambda systray: quit(systray, root),
    ):
        timer(root, myNeko, fps)
        root.mainloop()
