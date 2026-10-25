import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk

import yaml

from neko2020.application.animation_service import MIN_FPS
from neko2020.application.ports import IConfigProvider
from neko2020.infrastructure import files

_DESCRIPTION = (
    "Adjust how your pet looks and behaves.\n"
    "Click Apply (or Apply & Exit) to save — the pet restarts briefly "
    "to pick up the new settings.\n"
    "A backup of your previous config is saved as config.yml.bak."
)

_SECTIONS: list[tuple[str, str, list[tuple[str, str, type, int | None]]]] = [
    (
        "Appearance",
        "Which sprite set the pet uses.",
        [("animal", "Animal", str, None)],
    ),
    (
        "Movement",
        "How the pet chases the cursor and where it sits relative to it.",
        [
            ("speed.max", "Max Speed (px/frame)", int, None),
            ("speed.min", "Min Speed (px/frame)", int, None),
            ("offset.x", "Cursor Offset X (px)", int, None),
            ("offset.y", "Cursor Offset Y (px)", int, None),
            ("idle_space", "Idle Threshold (px)", int, None),
        ],
    ),
    (
        "Behavior Timing",
        "Number of sprite swaps spent in each idle action. Independent "
        "of FPS and Frame Hold.",
        [
            ("duration.stop", "Stop", int, None),
            ("duration.wash", "Wash", int, None),
            ("duration.scratch", "Scratch", int, None),
            ("duration.yawn", "Yawn", int, None),
            ("duration.awake", "Awake", int, None),
            ("duration.claw", "Claw", int, None),
            ("duration.awake_rand", "Awake Variance", int, None),
        ],
    ),
    (
        "Wandering",
        "Let a sleeping pet occasionally wake up and walk to a random "
        "spot instead of sleeping forever.",
        [
            ("wander.enabled", "Enable Wandering", bool, None),
            ("wander.sleep_time", "Sleep Before Wander", int, None),
            ("wander.rand", "Wander Variance", int, None),
        ],
    ),
    (
        "Performance",
        "Lower FPS reduces CPU usage; higher makes motion smoother.\n"
        "Frame Hold is how many ticks pass before the sprite image "
        "swaps — raise it if a high FPS makes the pet flicker.",
        [
            ("fps", "FPS", int, MIN_FPS),
            ("frame_hold", "Frame Hold (ticks)", int, 1),
        ],
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


def _parse_int_field(
    raw: str, label: str, min_val: int | None = None
) -> tuple[int | None, str | None]:
    """Parse `raw` as an int for `label`, applying an optional minimum.

    Returns (value, None) on success, or (None, error_message) on failure.
    Pure logic, kept free of Tkinter so it's unit-testable headlessly.
    """
    try:
        value = int(raw)
    except ValueError:
        return None, f"'{label}' must be an integer."
    if min_val is not None and value < min_val:
        return None, f"'{label}' must be at least {min_val}."
    return value, None


def _scale_for_fps(data: dict, ratio: float) -> None:
    """Rescale `data` in place after the fps changes by `ratio`.

    Frame Hold grows with fps and Max/Min Speed (px per tick) shrink, so
    the sprite swap rate and the on-screen speed stay the same in real
    time. Pure logic, kept free of Tkinter so it's unit-testable
    headlessly.
    """
    data["frame_hold"] = max(1, round(data["frame_hold"] * ratio))
    for key in ("max", "min"):
        data["speed"][key] = max(1, round(data["speed"][key] / ratio))


def _write_config(user_path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(user_path), exist_ok=True)
    if os.path.exists(user_path):
        shutil.copy2(user_path, user_path + ".bak")
    with open(user_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False)


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
        self._initial_fps: int | None = None

    def open(self) -> None:
        if self._win is not None:
            try:
                self._win.lift()
                self._win.focus_set()
                return
            except tk.TclError:
                self._win = None

        self._config.reload()
        self._initial_fps = self._config.get_int("fps")
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

            for i, (path, label, typ, _min_val) in enumerate(fields, start=1):
                tk.Label(tab, text=label + ":", anchor="w", width=22).grid(
                    row=i, column=0, sticky="w", pady=2
                )
                if typ is bool:
                    bool_var = tk.BooleanVar(value=self._config.get_bool(path))
                    self._vars[path] = bool_var
                    tk.Checkbutton(tab, variable=bool_var).grid(
                        row=i, column=1, sticky="w", pady=2, padx=(8, 0)
                    )
                    continue
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
        for path, label, typ, min_val in _all_fields():
            if typ is bool:
                _set_nested(data, path, bool(self._vars[path].get()))
                continue
            raw = str(self._vars[path].get()).strip()
            if typ is int:
                val, error = _parse_int_field(raw, label, min_val)
                if error is not None:
                    messagebox.showerror(
                        "Invalid value", error, parent=self._win
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
        self._maybe_scale_for_fps(data)
        _write_config(self._user_path, data)
        self._service.restart()
        self._initial_fps = data.get("fps", self._initial_fps)
        return True

    def _maybe_scale_for_fps(self, data: dict) -> None:
        new_fps = data.get("fps")
        if (
            new_fps is None
            or not self._initial_fps
            or new_fps == self._initial_fps
        ):
            return
        ratio = new_fps / self._initial_fps
        if not messagebox.askyesno(
            "Scale settings?",
            f"FPS changed from {self._initial_fps} to {new_fps} "
            f"(×{ratio:.3g}).\n\n"
            "Scale Frame Hold up and Max/Min Speed down by the same "
            "factor to keep the same real-time look and speed?",
            parent=self._win,
        ):
            return
        _scale_for_fps(data, ratio)
        for path, value in (
            ("frame_hold", data["frame_hold"]),
            ("speed.max", data["speed"]["max"]),
            ("speed.min", data["speed"]["min"]),
        ):
            self._vars[path].set(str(value))

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
