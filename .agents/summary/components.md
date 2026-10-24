---
title: Components
description: Major modules and their responsibilities
---

# Components

## `neko2020/__main__.py` — Composition Root

- Enumerates monitors (ctypes `EnumDisplayMonitors`) and creates a Tkinter window spanning the virtual screen
- Applies transparency, click-through, and Alt+Tab hiding; positions the window with `SetWindowPos`
- Builds `YamlConfigProvider`, `TkinterCursorProvider`, `AnimationService`, `ConfigDialog`, and the pystray tray menu (Config / Stop / Start / Restart / Quit)
- Supplies the session factory that creates a fresh `(NekoStateMachine, TkinterRenderer)` pair on each start/restart, starting the pet at the cursor's monitor

## `domain/state_machine.py` — NekoStateMachine

Central logic class; pure Python, no I/O. Responsibilities:

- `tick(cursor, position, size, bounds) -> TickResult(frame_index, x, y)` — the single domain call per frame
- Computes velocity toward the cursor, capped at `speed.max` and clamped to the monitor bounds (inset by half the sprite size)
- Direction chosen by dividing the circle into 8 sectors using `sin(pi/8)` thresholds
- Idle timers drive STOP → WASH (or *_CLAW at screen edges) → SCRATCH → YAWN → SLEEP; cursor movement beyond `idle_space` wakes the pet (AWAKE) before it chases
- Maps each `State` enum member to a 4-element list of integer frame indices

## `domain/value_objects.py` — Value Objects

Frozen dataclasses:

| Class | Fields |
|---|---|
| `Point` | `x`, `y` |
| `Size` | `cx`, `cy` |
| `Rect` | `left`, `top`, `right`, `bottom` (+ `width`/`height` properties) |

## `application/animation_service.py` — AnimationService

- Owns the tick loop via an injected scheduler (`root.after`)
- `start()` / `stop()` / `restart()` — tray- and dialog-driven lifecycle; restart waits for the loop to stop, then rebuilds the session
- Picks the monitor rect containing the cursor each tick so the pet stays on the active display
- Keeps an idle pump running while stopped so the Tk loop stays alive

## `application/ports.py` — Ports

ABCs decoupling the domain/application from Tkinter and YAML: `IConfigProvider` (`get_int/get_float/get_string/reload`), `ICursorProvider` (`get_cursor_position`), `IRenderer` (`render/get_position/get_size/get_bounds`).

## `adapters/tkinter_renderer.py` — TkinterRenderer

- Loads the 32 sprites for the configured animal (resolving `"random"` across bundled and user resource dirs)
- `render(frame_index, x, y)` redraws the single canvas image when the frame or position changed, converting screen coords to canvas coords

## `adapters/tkinter_cursor.py` — TkinterCursorProvider

- `get_cursor_position()` via `winfo_pointerx/y` (virtual-screen coordinates)

## `adapters/yaml_config.py` — YamlConfigProvider

- `reload()` loads `config/default_config.yml` and deep-merges the user config over it (BaseLoader: scalars stay strings; typed accessors convert)
- Dot-notation accessors: `get_int`, `get_float`, `get_string`

## `infrastructure/image_loader.py` — Image Loader

- `load_images(animal, scale, user_resource_base)` — returns the ordered list of 32 `ImageTk.PhotoImage` objects plus sprite width/height
- The ordered icon-name list is hard-coded here; filenames under `resource/<animal>/` must match exactly
- User resource dir (`~/.config/neko2020/resources/<animal>/`) takes priority over the bundled `resource/`

## `infrastructure/files.py` — File Helpers

- `get_project_root()`, `get_user_resource_dir()`
- `select_random_directory_merged(project_dir, user_dir)` — random animal across both locations

## `ui/config_dialog.py` — ConfigDialog

- Tray-opened Toplevel with tabbed sections (Appearance / Movement / Behavior Timing / Performance) generated from a declarative field list
- Animal field is a read-only combobox listing bundled + user sprite sets plus `"random"`
- Apply writes the user config (with `.bak` backup) and restarts the animation on a background thread
