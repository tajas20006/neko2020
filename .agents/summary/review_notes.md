---
title: Review Notes
description: Known gaps, platform limitations, and cleanup candidates
---

# Review Notes

## Completeness Gaps

### `speed.min` is unused
`NekoStateMachine` stores `min_speed` and the config dialog exposes "Min Speed", but nothing reads it — only `speed.max` affects movement. Either implement a behavior for it or remove it from the config, dialog, and constructor.

### Windows-only — no cross-platform path
The project description historically said "Cross-Platform," but the overlay setup uses Win32-specific ctypes calls (monitor enumeration, window styles, `SetWindowPos`) with no Linux/macOS code path. `pystray` and the ports-and-adapters structure would support adding one.

### Hard-coded icon name list
The ordered list of 32 icon names lives in `infrastructure/image_loader.py`; the per-state frame indices in `domain/state_machine.py` depend on that exact order. Anyone adding sprites must match both. The `tools/` generators produce conforming sets.

### UI layer untested
`ui/config_dialog.py` and `__main__.py` have no test coverage (they require a live Tk/Win32 environment). Domain, application, adapters, and infrastructure modules each have a test file under `tests/`.

## Cleanup Candidates

- `neko2020/utils/` may linger as an empty directory (only `__pycache__`) from the pre-layers refactor; the modules moved into `domain/`, `adapters/`, and `infrastructure/`.

## Recommendations

1. Resolve `speed.min` (implement or remove)
2. Consider extracting the movement math from `NekoStateMachine.tick()` into a dedicated domain helper to shrink the 140-line method and ease testing
3. If cross-platform support is ever wanted, add a platform adapter for the overlay window alongside the existing Tkinter adapters
