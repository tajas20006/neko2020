---
title: Data Models
description: Data structures used across the application
---

# Data Models

## Geometric Types (`domain/value_objects.py`)

Frozen dataclasses:

```python
Point(x: int, y: int)           # cursor or pet position
Size(cx: int, cy: int)          # sprite dimensions
Rect(left, top, right, bottom)  # monitor / virtual-screen bounds
                                #   (.width / .height properties)
```

## Animation State (`domain/state_machine.py`)

`State` is an `Enum` with 18 members:

```
STOP  WASH  SCRATCH  YAWN  SLEEP  AWAKE
U_MOVE  D_MOVE  L_MOVE  R_MOVE
UL_MOVE  UR_MOVE  DL_MOVE  DR_MOVE
U_CLAW  D_CLAW  L_CLAW  R_CLAW
```

## Tick Result

```python
@dataclass(frozen=True)
class TickResult:
    state: State       # current behavior state
    phase: int         # 0-3 position in the state's animation cycle
    x: int             # new pet center (screen coords)
    y: int
```

## Sprite Map

`adapters/sprite_map.py` maps each `(State, phase)` to an icon name. Example:

```python
{
    State.STOP:   ("yawn2",) * 4,
    State.R_MOVE: ("right1", "right2", "right1", "right2"),
    State.SLEEP:  ("sleep1", "sleep1", "sleep2", "sleep2"),
    ...
}
```

Names come from `ICON_NAMES` in `infrastructure/image_loader.py` (`"Awake"`, `"up1"`, …, `"sleep2"` — 32 names) and correspond directly to `.ico` filenames under `resource/<animal>/`.

## Configuration Dict

After loading and deep-merging YAMLs (`adapters/yaml_config.py`, BaseLoader — all scalars are strings until a typed accessor converts them):

```python
{
    "speed": {"max": 60},
    "offset": {"x": 0, "y": -35},
    "duration": {"stop": 4, "wash": 10, "scratch": 4, "yawn": 3,
                 "awake": 3, "claw": 10, "awake_rand": 20},
    "idle_space": 10,
    "animal": "neko",
    "fps": 4,
}
```

`fps` is frames per second — the tick delay is `1000 // fps` ms.

## Image List

`TkinterRenderer` holds the `dict[str, ImageTk.PhotoImage]` (keyed by icon name) returned by `load_images()`; `sprite_name(state, phase)` picks the key. Images are loaded once per session (start/restart), not per frame.
