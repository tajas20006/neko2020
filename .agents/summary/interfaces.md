---
title: Interfaces
description: Ports between layers, config YAML schema, sprite conventions, CI workflows
---

# Interfaces

## Application Ports (`application/ports.py`)

```python
class IConfigProvider(ABC):
    def get_int(path: str) -> int
    def get_float(path: str) -> float
    def get_string(path: str) -> str
    def reload() -> None

class ICursorProvider(ABC):
    def get_cursor_position() -> Point

class IRenderer(ABC):
    def render(frame_index: int, x: int, y: int) -> None
    def get_position() -> Point
    def get_size() -> Size
    def get_bounds() -> Rect
```

Implementations live in `adapters/` (`YamlConfigProvider`, `TkinterCursorProvider`, `TkinterRenderer`). Config paths use dot notation into the merged YAML tree (e.g., `"speed.max"`, `"duration.stop"`).

## Domain API (`domain/state_machine.py`)

```python
NekoStateMachine(*, stop_time, wash_time, scratch_time, yawn_time,
                 awake_time, claw_time, awake_rand, min_speed,
                 max_speed, idle_space, offset: Point)

NekoStateMachine.tick(
    cursor: Point,      # current cursor position
    position: Point,    # current pet position (from renderer)
    size: Size,         # sprite size (for boundary insets)
    bounds: Rect,       # monitor containing the cursor
) -> TickResult         # (frame_index, x, y)
```

`tick` is the only call per animation frame; `AnimationService` wires it to the renderer.

## AnimationService API (`application/animation_service.py`)

```python
AnimationService(config, cursor, session_factory, scheduler, monitors)
service.start()    # build session via factory, begin ticking
service.stop()     # halt ticks (idle pump keeps Tk alive)
service.restart()  # stop, wait, start — reloads config and sprites
```

## Configuration Interface

**Default config** (`config/default_config.yml`):

```yaml
speed:
  max: 60
  min: 2
offset:
  x: 0
  y: -35
duration:
  stop: 4
  wash: 10
  scratch: 4
  yawn: 3
  awake: 3
  claw: 10
  awake_rand: 20
idle_space: 10
animal: neko
fps: 4
```

**User config** location: `~/.config/neko2020/config.yml` (respects `XDG_CONFIG_HOME`). Any key overrides the default via deep merge. The tray **Config** dialog (`ui/config_dialog.py`) writes this file (backing up the previous version to `config.yml.bak`) and restarts the animation.

## Sprite Resource Interface

Each animal directory must contain exactly 32 `.ico` files named according to the hard-coded ordered list in `infrastructure/image_loader.py`. Lookup order: `~/.config/neko2020/resources/<animal>/` first, then bundled `resource/<animal>/`. `animal: random` picks a random directory across both. The `tools/` scripts generate conforming sets with AI (see `tools/README.md`).

## System Tray Interface

`pystray.Icon` menu in `__main__.py`:

| Label | Action |
|---|---|
| Config (default, double-click) | Open the settings dialog |
| Stop | Pause animation |
| Start | Resume animation (rebuilds session) |
| Restart | Reload config, recreate state machine + renderer |
| Quit | Exit the process |

## GitHub Actions / CI

- **ci.yml** — pytest + coverage upload to Codecov
- **build-exe.yml** — PyInstaller build; GitHub Release tagged with the `pyproject.toml` version (bump before merging to master)
- **claude.yml** — responds to `@claude` mentions in PR/issue comments
- **claude-code-review.yml** — automated review on every PR
