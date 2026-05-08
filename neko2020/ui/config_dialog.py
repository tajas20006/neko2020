import os
import shutil
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import yaml

from neko2020.application.ports import IConfigProvider
from neko2020.infrastructure import files

_FIELDS = [
    ("speed.max", "Max Speed", int),
    ("speed.min", "Min Speed", int),
    ("offset.x", "Offset X", int),
    ("offset.y", "Offset Y", int),
    ("duration.stop", "Stop Duration", int),
    ("duration.wash", "Wash Duration", int),
    ("duration.scratch", "Scratch Duration", int),
    ("duration.yawn", "Yawn Duration", int),
    ("duration.awake", "Awake Duration", int),
    ("duration.claw", "Claw Duration", int),
    ("duration.awake_rand", "Awake Rand Duration", int),
    ("idle_space", "Idle Space", int),
    ("fps", "FPS", int),
    ("animal", "Animal", str),
]


def _get_animals() -> list[str]:
    resource_dir = os.path.join(files.get_project_root(), "resource")
    try:
        return sorted(
            d
            for d in os.listdir(resource_dir)
            if os.path.isdir(os.path.join(resource_dir, d))
        )
    except OSError:
        return []


def _set_nested(d: dict, path: str, value) -> None:
    keys = path.split(".")
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


def _write_config(user_path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(user_path), exist_ok=True)
    if os.path.exists(user_path):
        shutil.copy2(user_path, user_path + ".bak")
    with open(user_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


class ConfigDialog:
    def __init__(
        self,
        parent: tk.Tk,
        config: IConfigProvider,
        user_path: str,
        service,
    ):
        self._parent = parent
        self._config = config
        self._user_path = user_path
        self._service = service
        self._win: tk.Toplevel | None = None

    def open(self) -> None:
        if self._win is not None:
            try:
                self._win.lift()
                self._win.focus_set()
                return
            except tk.TclError:
                self._win = None

        self._config.reload()
        animals = _get_animals()

        win = tk.Toplevel(self._parent)
        win.title("neko2020 Config")
        win.resizable(False, False)
        win.wm_attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", self._cancel)
        self._win = win

        frame = tk.Frame(win, padx=12, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        self._vars: dict[str, tk.Variable] = {}
        for row, (path, label, _typ) in enumerate(_FIELDS):
            tk.Label(frame, text=label + ":", anchor="w", width=18).grid(
                row=row, column=0, sticky="w", pady=2
            )
            value = self._config.get_string(path)
            var = tk.StringVar(value=value)
            self._vars[path] = var
            if path == "animal":
                combo = ttk.Combobox(
                    frame,
                    textvariable=var,
                    values=animals if animals else [value],
                    state="readonly",
                    width=18,
                )
                combo.grid(row=row, column=1, sticky="ew", pady=2, padx=(8, 0))
            else:
                tk.Entry(frame, textvariable=var, width=20).grid(
                    row=row, column=1, sticky="ew", pady=2, padx=(8, 0)
                )

        frame.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(win, padx=12, pady=8)
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Save", width=8, command=self._save).pack(
            side=tk.LEFT, padx=3
        )
        tk.Button(btn_frame, text="Apply", width=8, command=self._apply).pack(
            side=tk.LEFT, padx=3
        )
        tk.Button(
            btn_frame, text="Cancel", width=8, command=self._cancel
        ).pack(side=tk.LEFT, padx=3)

        win.focus_set()

    def _collect(self) -> dict | None:
        data: dict = {}
        for path, label, typ in _FIELDS:
            raw = self._vars[path].get().strip()
            if typ is int:
                try:
                    val: int | str = int(raw)
                except ValueError:
                    messagebox.showerror(
                        "Invalid value",
                        f"'{label}' must be an integer.",
                        parent=self._win,
                    )
                    return None
            else:
                val = raw
            _set_nested(data, path, val)
        return data

    def _do_save(self) -> bool:
        data = self._collect()
        if data is None:
            return False
        _write_config(self._user_path, data)
        threading.Thread(target=self._service.restart, daemon=True).start()
        return True

    def _save(self) -> None:
        if self._do_save():
            self._close()

    def _apply(self) -> None:
        self._do_save()

    def _cancel(self) -> None:
        self._close()

    def _close(self) -> None:
        if self._win is not None:
            self._win.destroy()
            self._win = None
