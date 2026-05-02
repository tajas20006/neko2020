---
title: Data Models
description: Data structures used across the application
---

# Data Models

## Geometric Types (`utils/classes.py`)

```python
Point(x: int, y: int)       # cursor or pet position
Size(cx: int, cy: int)      # screen or sprite dimensions
Rect(left, top, right, bottom)  # boundary rectangle
```

## Animation State

States are plain string constants defined at the top of `neko.py`:

```
STOP  WASH  SCRATCH  YAWN  SLEEP  AWAKE
U_MOVE  D_MOVE  L_MOVE  R_MOVE
UL_MOVE  UR_MOVE  DL_MOVE  DR_MOVE
U_CLAW  D_CLAW  L_CLAW  R_CLAW
```

## Frame Map

A dict in `neko.py` mapping each state string to a list of 2–4 icon name strings (the animation cycle). Example:

```python
{
    "R_MOVE": ["neko2R_1", "neko2R_2"],
    "STOP":   ["stop"],
    "WASH":   ["wash1", "wash2"],
    ...
}
```

Icon names correspond directly to filenames under `resource/<animal>/`.

## Configuration Dict

After loading and deep-merging YAMLs, the config is a nested dict:

```python
{
    "speed": {"max": 60, "min": 2},
    "offset": {"x": 0, "y": -50},
    "time": {"stop": 4, "wash": 10, ...},
    "idle_space": 10,
    "animal": "neko",
    "fps": 300
}
```

## Image Cache

`Pet` maintains a dict `{icon_name: ImageTk.PhotoImage}` to avoid re-loading `.ico` files on every frame update.
