# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Documentation

Always read `AGENTS.md` and any files under `.agents/` at the start of a task for project context, conventions, and agent-specific instructions.

## Commands

```bash
# Install dependencies (creates uv.lock)
uv sync

# Run the app from source
uv run python -m neko2020

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_state_machine.py::test_full_idle_sequence

# Build standalone executable
uv run pyinstaller neko2020.spec   # output: dist/neko2020.exe

# Lint / format (also runs automatically via pre-commit)
uv run ruff check neko2020/ tests/
uv run ruff format neko2020/ tests/

# Install pre-commit hooks (first-time setup)
uv run pre-commit install
```

## Architecture

The application is a Windows-only transparent fullscreen overlay organized in clean-architecture layers. Understanding how it achieves transparency and click-through is essential before touching `__main__.py`:

- Tkinter window is set to `'-transparentcolor green'` (the green background becomes invisible)
- `root.wm_attributes("-disabled", True)` plus Win32 styles make mouse events pass through to the desktop
- `WS_EX_TOOLWINDOW` (applied via ctypes) hides the window from Alt+Tab
- The window spans the virtual screen across all monitors; `EnumDisplayMonitors` provides per-display bounds and `SetWindowPos` positions the window (Tk `geometry()` can't express negative coordinates)

The animation loop runs on Tkinter's `after()` scheduler (not a separate thread). The system tray icon (`pystray`) runs detached on its own thread.

**Layers** (dependencies point inward only):

```
domain/         # Pure logic, no I/O: state_machine.py, value_objects.py
application/    # Orchestration: animation_service.py, ports.py (ABCs)
adapters/       # Port implementations: tkinter_renderer.py,
                #   tkinter_cursor.py, yaml_config.py
infrastructure/ # Filesystem/resources: files.py, image_loader.py
ui/             # config_dialog.py (tray-opened settings GUI)
__main__.py     # Composition root: window setup, wiring, tray menu
```

**Core flow per frame:**

```
AnimationService._tick()
  → NekoStateMachine.tick(cursor, position, size, bounds)
      returns TickResult(frame_index, x, y)
  → TkinterRenderer.render(frame_index, x, y)
      swaps PhotoImage on the canvas
  → scheduler re-arms root.after(1000 // fps, ...)
```

`NekoStateMachine` (`domain/state_machine.py`) owns all behavior logic: an 18-state machine (`STOP`, `WASH`, `SCRATCH`, `YAWN`, `SLEEP`, `AWAKE`, 8 directional moves, 4 claw states) as a `State` enum. Direction to the cursor is computed by dividing the circle into 8 sectors with `math.sin(math.pi / 8)`. Each state maps to a 4-element list of integer frame indices; the indices point into the ordered 32-icon list hard-coded in `infrastructure/image_loader.py`, whose names must exactly match filenames under `resource/<animal>/`.

`TkinterRenderer` (`adapters/tkinter_renderer.py`) is purely visual: it loads the 32 `.ico` sprites via Pillow, keeps `ImageTk.PhotoImage` objects, and redraws a single canvas item when the frame or position changes.

## Configuration

User config at `~/.config/neko2020/config.yml` (respects `XDG_CONFIG_HOME`) deep-merges over `config/default_config.yml`. Key values: `speed.max`, `speed.min`, `fps` (frames per second; tick delay is `1000 // fps` ms), `animal` (subdirectory name under `resource/`, or `"random"`), timing values under `duration.*`, `offset.x`/`offset.y`, `idle_space`. Users normally edit settings through the tray's **Config** dialog (`ui/config_dialog.py`), which writes the user config and restarts the animation.

## Adding a New Animal

Create `resource/<name>/` (or `~/.config/neko2020/resources/<name>/` for user-local sets) with all 32 `.ico` files. File names must exactly match the hard-coded list in `neko2020/infrastructure/image_loader.py`. Set `animal: <name>` in user config or use `"random"` to include it in random rotation. Scripts under `tools/` can generate sprite sets with AI (see `tools/README.md`).

## Code Style

- Ruff format with 79-character line length (enforced by pre-commit)
- Ruff lint (E/F/W rules, enforced by pre-commit)

## Git Workflow

- Always branch from `develop`, not `master`
- Always target `develop` as the PR base branch
