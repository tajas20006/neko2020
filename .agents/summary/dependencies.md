---
title: Dependencies
description: External dependencies and their usage
---

# Dependencies

## Runtime

| Package | Version | Usage |
|---|---|---|
| `pyyaml` | >=6.0.3 | Parsing `config/*.yml` and user config |
| `pystray` | >=0.19.5 | System tray icon and menu (runs detached) |
| `pillow` | >=12.2.0 | Loading `.ico` sprites; `ImageTk.PhotoImage` for Tkinter |

## Optional Extras (sprite generation, `tools/`)

| Extra | Packages | Usage |
|---|---|---|
| `imgen` | torch, torchvision, diffusers, transformers, accelerate, safetensors, ollama, rembg | Local Stable Diffusion sprite generation (CUDA GPU) |
| `imgen-gpt` | openai, rembg | OpenAI gpt-image sprite generation |

## Standard Library (key modules)

| Module | Usage |
|---|---|
| `tkinter` | Transparent overlay window, canvas drawing, config dialog |
| `ctypes` | Win32 calls: `EnumDisplayMonitors`, `SetWindowLongW`, `SetWindowPos` |
| `math`, `random` | 8-directional angle calculation; timing jitter; random animal |
| `abc` | Port interfaces in `application/ports.py` |
| `threading` | Restart synchronization (`Event`); dialog-triggered restart thread |

## Development (dependency-group `dev`)

| Package | Usage |
|---|---|
| `pytest` | Test runner (CI uploads coverage to Codecov) |
| `ruff` | Formatter + linter (79-char lines, E/F/W rules) |
| `pre-commit` | Git hooks running ruff format + lint |
| `pyinstaller` | Compiles to standalone `dist/neko2020.exe` |
| `pywin32`, `pywin32-ctypes`, `pefile` | Windows build support (win32 only markers) |

## CI

| Workflow | Usage |
|---|---|
| `ci.yml` | Runs pytest with coverage → Codecov |
| `build-exe.yml` | Builds the exe and creates a GitHub Release tagged from `pyproject.toml` version (master) |
| `claude.yml` | Responds to `@claude` mentions via `anthropics/claude-code-action@v1` |
| `claude-code-review.yml` | Automated review on every PR |
| Dependabot | Dependency update PRs (uv + GitHub Actions) |

## Platform Constraints

- Runtime is **Windows-only** — the overlay setup in `__main__.py` uses Win32 ctypes calls with no non-Windows code path (pystray itself is cross-platform)
- Python `>=3.12,<3.14` required
- Package management via **uv** (`uv.lock`); build backend hatchling
