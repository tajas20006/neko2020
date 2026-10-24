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
| [architecture.md](architecture.md) | Clean-architecture layers; how the transparent overlay works; animation loop design |
| [components.md](components.md) | What each module/class in the layered package does |
| [interfaces.md](interfaces.md) | Port ABCs between layers; config YAML schema; sprite resource conventions; CI workflows |
| [data_models.md](data_models.md) | State enum, frame index map, TickResult, geometric types |
| [workflows.md](workflows.md) | Startup sequence, per-tick flow, idle transitions, config-change flow, dev/build commands, adding animals |
| [dependencies.md](dependencies.md) | All runtime/optional/dev dependencies and platform constraints |
| [review_notes.md](review_notes.md) | Known gaps (unused `speed.min`, untested UI), platform limitations, cleanup candidates |

## Quick Reference

- **Technology**: Python 3.12+, Tkinter, Pillow, pystray, ctypes (Win32), PyInstaller, uv
- **Platform**: Windows-only at runtime
- **Entry point**: `neko2020/__main__.py` (also `python -m neko2020`)
- **State machine**: `neko2020/domain/state_machine.py` — `NekoStateMachine`, 18 states
- **Renderer**: `neko2020/adapters/tkinter_renderer.py`
- **Config path**: `~/.config/neko2020/config.yml` (tray Config dialog writes it)
- **Sprites**: `resource/<animal>/` or `~/.config/neko2020/resources/<animal>/` — 32 `.ico` files per animal

## Example Queries

- "How do I add a new animal?" → [workflows.md](workflows.md) § Adding a New Animal Type
- "How does the window stay transparent?" → [architecture.md](architecture.md) § Transparent Overlay Window
- "What does `tick()` return?" → [interfaces.md](interfaces.md) § Domain API, or [data_models.md](data_models.md) § Tick Result
- "What config keys exist?" → [interfaces.md](interfaces.md) § Configuration Interface
- "How does the config dialog apply changes?" → [workflows.md](workflows.md) § Config Change
- "Why is there no Linux support?" → [review_notes.md](review_notes.md)
