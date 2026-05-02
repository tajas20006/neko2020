---
title: Dependencies
description: External dependencies and their usage
---

# Dependencies

## Runtime

| Package | Version | Usage |
|---|---|---|
| `pyyaml` | ^6.0.2 | Parsing `config/*.yml` and user config |
| `infi-systray` | ^0.1.12 | Windows system tray icon and menu |
| `pillow` | ^10.4.0 | Loading `.ico` sprite files; `ImageTk.PhotoImage` for Tkinter |

## Standard Library (key modules)

| Module | Usage |
|---|---|
| `tkinter` | Fullscreen transparent window, canvas drawing |
| `ctypes` | Windows API calls (`SetWindowLong`, `GetCursorPos`, transparency) |
| `math` | `sin`/`atan2` for 8-directional angle calculation |
| `os`, `pathlib` | Resource path resolution |
| `threading` | System tray runs on a background thread |

## Build / Distribution

| Package | Version | Usage |
|---|---|---|
| `pyinstaller` | ^6.10.0 | Compiles to standalone `dist/neko2020.exe` |
| `pywin32-ctypes` | ^0.2.3 | Required by PyInstaller on Windows |
| `pefile` | ^2024.8.26 | PE file manipulation (PyInstaller support) |
| `pywin32` | ^306 | Windows API bindings |

## Development

| Package | Version | Usage |
|---|---|---|
| `pytest` | ^8.3.3 | Test runner |
| `black` | ^24.8.0 | Auto-formatter (79-char line length) |
| `flake8` | ^7.1.1 | Linter |
| `pre-commit` | ^3.8.0 | Git hooks (runs black + flake8 on commit) |

## CI

| Tool | Usage |
|---|---|
| `anthropics/claude-code-action@v1` | AI-powered PR assistant and code review via GitHub Actions |
| Dependabot | Daily pip dependency updates (max 10 open PRs) |

## Platform Constraints

- Runtime is **Windows-only** (`ctypes` calls use Win32 API, `infi-systray` is Windows-only)
- Python `>=3.12,<3.14` required
