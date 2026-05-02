---
title: Knowledge Base Index
description: Primary index for AI assistants — describes all documentation files and when to consult each
---

# neko2020 — Knowledge Base Index

## How to Use This Documentation

Load this file first. Each entry below summarizes a documentation file so you can decide whether to read the full file before answering a question.

## Documentation Files

| File | When to Read |
|---|---|
| [codebase_info.md](codebase_info.md) | Quick project metadata — version, stack, directory layout |
| [architecture.md](architecture.md) | How the transparent overlay window works; the overall process model; animation loop design |
| [components.md](components.md) | What each Python module/class does and its public methods |
| [interfaces.md](interfaces.md) | Public APIs between modules; config YAML schema; sprite resource conventions; CI workflows |
| [data_models.md](data_models.md) | State constants, frame map, geometric types, image cache |
| [workflows.md](workflows.md) | Startup sequence, per-tick animation flow, idle state transitions, dev/build commands, adding animals |
| [dependencies.md](dependencies.md) | All runtime/build/dev dependencies and platform constraints |
| [review_notes.md](review_notes.md) | Known gaps in tests and documentation; platform limitations |

## Quick Reference

- **Technology**: Python 3.12+, Tkinter, Pillow, ctypes (Win32), PyInstaller
- **Platform**: Windows-only at runtime
- **Entry point**: `neko2020/__main__.py` (also `python -m neko2020`)
- **State machine**: `neko2020/neko.py` — 18 states
- **Renderer**: `neko2020/pet.py`
- **Config path**: `~/.config/neko2020/config.yml`
- **Sprites**: `resource/<animal>/` — 32 `.ico` files per animal

## Example Queries

- "How do I add a new animal?" → [workflows.md](workflows.md) § Adding a New Animal Type
- "How does the window stay transparent?" → [architecture.md](architecture.md) § Transparent Overlay Window
- "What does `tick()` return?" → [interfaces.md](interfaces.md) § Neko class, or [components.md](components.md) § neko.py
- "What config keys exist?" → [interfaces.md](interfaces.md) § Configuration Interface
- "Why is there no Linux support?" → [review_notes.md](review_notes.md)
