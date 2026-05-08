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
uv run pytest tests/test_neko2020.py::test_version

# Build standalone executable
uv run pyinstaller neko2020.spec   # output: dist/neko2020.exe

# Lint / format (also runs automatically via pre-commit)
uv run ruff check neko2020/ tests/
uv run ruff format neko2020/ tests/

# Install pre-commit hooks (first-time setup)
uv run pre-commit install
```

## Architecture

The application is a Windows-only transparent fullscreen overlay. Understanding how it achieves transparency and click-through is essential before touching `__main__.py`:

- Tkinter window is set to `'-transparentcolor green'` (the green background becomes invisible)
- `ctypes.windll.user32.SetWindowLong` applies `WS_EX_TRANSPARENT | WS_EX_LAYERED` so mouse events pass through to the desktop
- `WS_EX_TOOLWINDOW` hides the window from Alt+Tab

The animation loop runs on Tkinter's `after()` scheduler (not a separate thread). Each tick calls `Neko.tick(cursor)` then `Pet.update(state, frame, x, y)`.

**Core flow:**

```
__main__.py  →  Neko.tick()  →  returns (state, frame_name, x, y)
             →  Pet.update()  →  swaps PhotoImage on canvas
```

`Neko` (`neko.py`) owns all behavior logic: an 18-state machine (`STOP`, `WASH`, `SCRATCH`, `YAWN`, `SLEEP`, `AWAKE`, 8 directional moves, 4 claw states). Direction to the cursor is computed by dividing the circle into 8 sectors with `math.sin(math.pi / 8)`. Frame names are hard-coded lists per state; the names must exactly match filenames under `resource/<animal>/`.

`Pet` (`pet.py`) is purely visual: it loads 32 `.ico` sprites via Pillow, caches `ImageTk.PhotoImage` objects, and moves/swaps a single canvas item each frame.

## Configuration

User config at `~/.config/neko2020/config.yml` deep-merges over `config/default_config.yml`. Key values: `speed.max`, `speed.min`, `fps` (ms between frames), `animal` (subdirectory name under `resource/`, or `"random"`), timing values under `time.*`.

## Adding a New Animal

Create `resource/<name>/` with all 32 `.ico` files. File names must exactly match the hard-coded list in `neko2020/utils/images.py`. Set `animal: <name>` in user config or use `"random"` to include it in random rotation.

## Code Style

- Ruff format with 79-character line length (enforced by pre-commit)
- Ruff lint (E/F/W rules, enforced by pre-commit)

## Git Workflow

- Always branch from `develop`, not `master`
- Always target `develop` as the PR base branch
