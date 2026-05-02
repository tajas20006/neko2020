---
title: Interfaces
description: Public APIs between modules and external integration points
---

# Interfaces

## Module-Level APIs

### `Neko` class (`neko.py`)

```python
Neko(config: Config, screen: Size) -> Neko
Neko.tick(cursor: Point) -> (state: str, frame: str, x: int, y: int)
```

`tick` is the only public method called each animation frame.

### `Pet` class (`pet.py`)

```python
Pet(root: Tk, config: Config) -> Pet
Pet.update(state: str, frame: str, x: int, y: int) -> None
Pet.get_boundary() -> Rect
```

`update` swaps the displayed sprite; `get_boundary` returns current screen bounds.

### Config API (`utils/configs.py`)

```python
get_int(path: str) -> int
get_float(path: str) -> float
get_str(path: str) -> str
```

Dot-notation paths into the merged YAML tree (e.g., `"speed.max"`, `"animal"`).

## Configuration Interface

**Default config** (`config/default_config.yml`):

```yaml
speed:
  max: 60
  min: 2
offset:
  x: 0
  y: -50
time:
  stop: 4
  wash: 10
  scratch: 4
  yawn: 3
  awake: 3
  claw: 10
  awake_rand: 20
idle_space: 10
animal: neko
fps: 300
```

**User config** location: `~/.config/neko2020/config.yml` (or `$XDG_CONFIG_HOME/neko2020/config.yml`). Any key overrides the default.

## Sprite Resource Interface

Each animal directory under `resource/<animal>/` must contain exactly 32 `.ico` files named according to the hard-coded list in `utils/images.py`. Adding a new animal type requires a directory with all 32 frames.

## System Tray Interface

The system tray icon exposes four commands via `infi-systray`:

| Label | Action |
|---|---|
| Start | Resume animation |
| Stop | Pause animation |
| Restart | Recreate Neko and Pet |
| Quit | Exit the process |

## GitHub Actions / CI

Two workflows in `.github/workflows/`:

- **claude.yml** — Responds to `@claude` mentions in PR/issue comments using `anthropics/claude-code-action@v1`
- **claude-code-review.yml** — Runs automated code review on every PR using the same action with `code-review` plugin
