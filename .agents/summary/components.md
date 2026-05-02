---
title: Components
description: Major modules and their responsibilities
---

# Components

## `neko2020/__main__.py` — Entry Point

- Creates full-screen transparent Tkinter window
- Applies Windows API flags for click-through and Alt+Tab hiding
- Builds system tray icon with Start / Stop / Restart / Quit callbacks
- Starts the animation loop via `root.after(fps, tick)`
- Instantiates `Neko` and `Pet`; calls them each tick

## `neko2020/neko.py` — Neko (State Machine)

Central logic class. Responsibilities:

- Tracks pet position (`x`, `y`) and current `state`
- Each `tick()` call: reads cursor position, calculates direction angle, chooses next state, advances animation frame
- Direction chosen by dividing the circle into 8 sectors using `math.sin(math.pi / 8)`
- Frame index cycles through a 4-element list per state (e.g., `[neko2R_1, neko2R_2]` for right movement)
- Idle timers count ticks to transition STOP → WASH → SCRATCH → YAWN → SLEEP

## `neko2020/pet.py` — Pet (Renderer)

- Holds a Tkinter `Canvas` and a `PhotoImage` item
- `update(state, frame, x, y)` swaps the image and moves the canvas item
- Caches loaded `ImageTk.PhotoImage` objects to avoid re-loading
- Reads `animal` from config; if `"random"`, picks a random resource subdirectory at startup

## `neko2020/utils/configs.py` — Config

- Loads `config/default_config.yml` at import time
- Deep-merges with `~/.config/neko2020/config.yml` (or `$XDG_CONFIG_HOME/neko2020/config.yml`) if present
- `get_int(path)`, `get_float(path)`, `get_str(path)` — dot-notation accessors

## `neko2020/utils/images.py` — Image Loader

- `load_images(animal, size)` — returns a dict mapping icon-name → `ImageTk.PhotoImage`
- Looks up sprites under `resource/<animal>/`
- Icon names are hard-coded in a fixed list matching the standard animation sequence

## `neko2020/utils/classes.py` — Data Classes

Simple named tuples:

| Class | Fields |
|---|---|
| `Point` | `x`, `y` |
| `Size` | `cx`, `cy` |
| `Rect` | `left`, `top`, `right`, `bottom` |

## `neko2020/utils/files.py` — File Helpers

- `get_project_root()` — returns the directory containing the package
- `select_random_directory(path)` — returns a random subdirectory path (used for random animal)
