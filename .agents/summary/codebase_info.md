---
title: Codebase Info
description: Basic metadata about the neko2020 project
---

# neko2020 — Codebase Info

| Field | Value |
|---|---|
| Name | neko2020 |
| Version | 0.1.2 |
| Language | Python 3.12+ |
| License | MIT |
| Build System | Poetry |
| Repository | https://github.com/tajas20006/neko2020 |

## Description

Cross-platform desktop pet (oneko-style) implemented in Python. A transparent overlay window renders an animated sprite that chases the mouse cursor, with system tray controls and 50+ configurable animal types.

## Directory Layout

```
neko2020/
├── neko2020/          # Main source package
│   ├── __main__.py    # Entry point, Tkinter window & system tray
│   ├── neko.py        # State machine & movement logic
│   ├── pet.py         # Visual rendering (canvas + sprites)
│   └── utils/         # Data classes, config, file helpers, image loader
├── config/            # default_config.yml
├── resource/          # 50+ animal sprite sets (32 .ico frames each)
├── tests/             # pytest test suite
└── .github/workflows/ # Claude Code GitHub Actions CI
```

## Technology Stack

- **GUI**: Tkinter (transparent overlay, canvas drawing)
- **Images**: Pillow (PIL)
- **Config**: PyYAML
- **System Tray**: infi-systray
- **Windows API**: ctypes, pywin32
- **Distribution**: PyInstaller (single .exe)
- **Quality**: black, flake8, pre-commit
