---
title: Review Notes
description: Known gaps, platform limitations, and cleanup candidates
---

# Review Notes

## Completeness Gaps

### Windows-only — no cross-platform path
The project description historically said "Cross-Platform," but the overlay setup uses Win32-specific ctypes calls (monitor enumeration, window styles, `SetWindowPos`) with no Linux/macOS code path. `pystray` and the ports-and-adapters structure would support adding one.

### Hard-coded icon name list
The 32 required icon names live in `ICON_NAMES` in `infrastructure/image_loader.py`; `adapters/sprite_map.py` refers to them by name (a test checks every mapped name exists). Anyone adding sprites must match that list. The `tools/` generators produce conforming sets.

### UI layer untested
`ui/config_dialog.py` and `__main__.py` have no test coverage (they require a live Tk/Win32 environment). Domain, application, adapters, and infrastructure modules each have a test file under `tests/`.

## Cleanup Candidates

- `neko2020/utils/` may linger as an empty directory (only `__pycache__`) from the pre-layers refactor; the modules moved into `domain/`, `adapters/`, and `infrastructure/`.

## Recommendations

1. Consider extracting the movement math from `NekoStateMachine.tick()` into a dedicated domain helper to shrink the 140-line method and ease testing
2. If cross-platform support is ever wanted, add a platform adapter for the overlay window alongside the existing Tkinter adapters
