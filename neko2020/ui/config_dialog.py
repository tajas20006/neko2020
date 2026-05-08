import os
import shutil
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import yaml

from neko2020.application.ports import IConfigProvider
from neko2020.infrastructure import files

_DESCRIPTION = (
    "Adjust how your pet looks and behaves.\n"
    "Click Apply (or Apply & Exit) to save — the pet restarts briefly "
    "to pick up the new settings.\n"
    "A backup of your previous config is saved as config.yml.bak."
)

_SECTIONS: list[tuple[str, str, list[tuple[str, str, type]]]] = [
    (
        "Appearance",
        "Which sprite set the pet uses.",
        [("animal", "Animal", str)],
    ),
    (
        "Movement",
        "How the pet chases the cursor and where it sits relative to it.",
        [
            ("speed.max", "Max Speed (px/frame)", int),
            ("speed.min", "Min Speed (px/frame)", int),
            ("offset.x", "Cursor Offset X (px)", int),
            ("offset.y", "Cursor Offset Y (px)", int),
            ("idle_space", "Idle Threshold (px)", int),
        ],
    ),
    (
        "Behavior Timing",
        "Number of animation frames spent in each idle action.",
        [
            ("duration.stop", "Stop", int),
            ("duration.wash", "Wash", int),
            ("duration.scratch", "Scratch", int),
            ("duration.yawn", "Yawn", int),
            ("duration.awake", "Awake", int),
            ("duration.claw", "Claw", int),
            ("duration.awake_rand", "Awake Variance", int),
        ],
    ),
    (
        "Performance",
        "Lower FPS reduces CPU usage; higher makes motion smoother.",
        [("fps", "FPS", int)],
    ),
]


def _all_fields():
    for _, _, fields in _SECTIONS:
        yield from fields


def _get_animals() -> list[str]:
    dirs: set[str] = set()
    for base in (
        os.path.join(files.get_project_root(), "resource"),
        files.get_user_resource_dir(),
    ):
        try:
            dirs.update(
                d
                for d in os.listdir(base)
                if os.path.isdir(os.path.join(base, d))
            )
        except OSError:
            pass
    return ["random"] + sorted(dirs)


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
        # Not topmost: the transparent root overlay stays on top so the
        # pet sprite appears in front while mouse events pass through it.
        win.protocol("WM_DELETE_WINDOW", self._cancel)
        self._win = win

        outer = tk.Frame(win, padx=14, pady=12)
        outer.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            outer,
            text=_DESCRIPTION,
            wraplength=380,
            justify=tk.LEFT,
            fg="#444444",
        ).pack(anchor="w", pady=(0, 10))

        ttk.Separator(outer, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=(0, 10)
        )

        self._vars: dict[str, tk.Variable] = {}

        notebook = ttk.Notebook(outer)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        for section_title, section_desc, fields in _SECTIONS:
            tab = tk.Frame(notebook, padx=10, pady=8)
            notebook.add(tab, text=section_title)

            tk.Label(
                tab,
                text=section_desc,
                fg="#666666",
                font=("TkDefaultFont", 8),
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

            for i, (path, label, _typ) in enumerate(fields, start=1):
                tk.Label(tab, text=label + ":", anchor="w", width=22).grid(
                    row=i, column=0, sticky="w", pady=2
                )
                value = self._config.get_string(path)
                var = tk.StringVar(value=value)
                self._vars[path] = var
                if path == "animal":
                    combo = ttk.Combobox(
                        tab,
                        textvariable=var,
                        values=animals if animals else [value],
                        state="readonly",
                        width=18,
                    )
                    combo.grid(
                        row=i, column=1, sticky="w", pady=2, padx=(8, 0)
                    )
                else:
                    tk.Entry(tab, textvariable=var, width=10).grid(
                        row=i, column=1, sticky="w", pady=2, padx=(8, 0)
                    )

        ttk.Separator(outer, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=(0, 10)
        )

        btn_frame = tk.Frame(outer)
        btn_frame.pack(anchor="w")
        tk.Button(
            btn_frame, text="Apply & Exit", width=12, command=self._save
        ).pack(side=tk.LEFT, padx=(0, 4))
        tk.Button(btn_frame, text="Apply", width=8, command=self._apply).pack(
            side=tk.LEFT, padx=(0, 4)
        )
        tk.Button(btn_frame, text="Exit", width=8, command=self._cancel).pack(
            side=tk.LEFT
        )

        win.focus_set()

    def _collect(self) -> dict | None:
        data: dict = {}
        for path, label, typ in _all_fields():
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
