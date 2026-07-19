---
title: Codebase Info
description: Basic metadata about the neko2020 project
---

# neko2020 — Codebase Info

| Field | Value |
|---|---|
| Name | neko2020 |
| Version | 0.2.1 |
| Language | Python >=3.12,<3.14 |
| License | MIT |
| Build System | uv + hatchling |
| Repository | https://github.com/tajas20006/neko2020 |

## Description

Desktop pet (oneko-style) for Windows implemented in Python. A transparent overlay window spanning all monitors renders an animated sprite that chases the mouse cursor, with system tray controls, a settings dialog, and 70+ animal sprite sets (plus AI generators for custom sets).

## Directory Layout

```
neko2020/
├── neko2020/            # Main source package (clean-architecture layers)
│   ├── __main__.py      # Composition root: window, tray, wiring
│   ├── domain/          # state_machine.py, value_objects.py (pure logic)
│   ├── application/     # animation_service.py, ports.py (ABCs)
│   ├── adapters/        # tkinter_renderer.py, tkinter_cursor.py,
│   │                    #   yaml_config.py
│   ├── infrastructure/  # files.py, image_loader.py
│   └── ui/              # config_dialog.py
├── config/              # default_config.yml
├── resource/            # 70+ animal sprite sets (32 .ico frames each)
├── tools/               # AI sprite-set generation scripts
├── tests/               # pytest test suite (per-module test files)
└── .github/workflows/   # CI, release build, Claude Code actions
```

## Technology Stack

- **GUI**: Tkinter (transparent overlay, canvas drawing, config dialog)
- **Images**: Pillow (PIL)
- **Config**: PyYAML
- **System Tray**: pystray
- **Windows API**: ctypes (monitor enumeration, window styles)
- **Distribution**: PyInstaller (single .exe, released via GitHub Actions)
- **Quality**: ruff (format + lint), pre-commit, pytest + Codecov
