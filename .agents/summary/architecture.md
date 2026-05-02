---
title: Architecture
description: System architecture, design patterns, and Windows overlay approach
---

# Architecture

## High-Level Overview

neko2020 is a single-process desktop application. The main thread runs a Tkinter event loop; a background thread drives the animation timer.

```mermaid
graph TB
    subgraph OS["Windows OS"]
        Cursor[Mouse Cursor]
        SysTray[System Tray]
    end

    subgraph App["neko2020 process"]
        Main["__main__.py\nTkinter window + timer"]
        Neko["neko.py\nState machine"]
        Pet["pet.py\nCanvas renderer"]
        Config["utils/configs.py\nYAML config"]
        Images["utils/images.py\nSprite loader"]
    end

    Cursor -->|position poll| Main
    Main -->|tick| Neko
    Neko -->|state + position| Pet
    Pet -->|draw icon| Main
    Config -->|settings| Main
    Config -->|settings| Neko
    Images -->|PIL ImageTk| Pet
    Main <-->|start/stop/quit| SysTray
```

## Transparent Overlay Window

The entire screen is covered by a single Tkinter window. Transparency is achieved by assigning a "transparent color" (green) to the window background and calling the Windows API to make that color invisible:

```
root.attributes('-transparentcolor', 'green')
root.attributes('-topmost', True)
root.attributes('-fullscreen', True)
```

Mouse and keyboard events pass through the window via Windows API `SetWindowLong` flags (`WS_EX_TRANSPARENT | WS_EX_LAYERED`). The window is hidden from Alt+Tab with `WS_EX_TOOLWINDOW`.

## Animation Loop

The Tkinter `after()` method drives the main animation loop at a configurable interval (default 300 ms). Each tick:

1. Query cursor position
2. Call `Neko.tick()` to update state and position
3. Call `Pet.update()` to re-draw the sprite frame on the canvas

## State Machine (neko.py)

```mermaid
stateDiagram-v2
    [*] --> STOP
    STOP --> WASH: idle_time >= stop_time
    WASH --> SCRATCH: wash done
    SCRATCH --> YAWN: scratch done
    YAWN --> SLEEP: yawn done
    SLEEP --> AWAKE: cursor moved
    AWAKE --> [direction_move]: cursor far enough
    [direction_move] --> STOP: near cursor
    STOP --> [direction_move]: cursor moved
    AWAKE --> STOP: cursor close
    SLEEP --> AWAKE: cursor moved
```

18 states total: `STOP`, `WASH`, `SCRATCH`, `YAWN`, `SLEEP`, `AWAKE`, `*_CLAW` (×4), and 8 directional movement states.

## Design Patterns

- **State machine** — `Neko` owns all behavioral logic; `Pet` only renders
- **Observer-lite** — `__main__` owns the tick and passes data down; no event bus
- **Resource embedding** — PyInstaller bundles the entire `resource/` tree into the .exe
