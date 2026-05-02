---
title: Review Notes
description: Documentation review: consistency and completeness findings
---

# Review Notes

## Consistency

No inconsistencies found across the generated documentation files.

## Completeness Gaps

### Minimal test coverage
`tests/test_neko2020.py` contains only a version assertion. The state machine (`neko.py`) and config merge logic (`utils/configs.py`) have no test coverage. Any agent helping with testing should note this gap.

### Hard-coded icon name list
`utils/images.py` contains a hard-coded list of 32 icon names. This list is not documented anywhere — anyone adding a new animal type must reverse-engineer it from the source. Consider extracting it to a constant or config.

### Windows-only — no cross-platform path
Despite the project description saying "Cross-Platform," the implementation uses Windows-specific APIs exclusively (`ctypes` Win32 calls, `infi-systray`). There is no Linux/macOS code path. This discrepancy is not noted in the README.

### No dual-monitor support
README notes this limitation but there is no tracking issue or planned fix documented.

### Per-animal config override
README mentions per-animal config customization but the implementation does not clearly support it. Worth verifying.

## Recommendations

1. Add unit tests for `Neko` state transitions and `configs.py` deep merge
2. Document the required 32 icon names in `interfaces.md` or a dedicated sprite spec
3. Update project description to clarify Windows-only status
