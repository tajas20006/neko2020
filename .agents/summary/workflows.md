---
title: Workflows
description: Key runtime and development workflows
---

# Workflows

## Application Startup

```mermaid
sequenceDiagram
    participant OS as Windows OS
    participant Main as __main__.py
    participant Config as configs.py
    participant Pet as pet.py
    participant Neko as neko.py

    Main->>Config: load default + user config
    Main->>OS: create fullscreen Tkinter window
    Main->>OS: apply WS_EX_TRANSPARENT flags (ctypes)
    Main->>Pet: Pet(root, config)
    Pet->>Pet: load sprites for animal
    Main->>Neko: Neko(config, screen_size)
    Main->>OS: register system tray icon
    Main->>Main: root.after(fps, tick)
    Main->>Main: root.mainloop()
```

## Animation Tick (per frame)

```mermaid
sequenceDiagram
    participant Main as __main__.py
    participant Neko as neko.py
    participant Pet as pet.py
    participant OS as Windows OS

    Main->>OS: GetCursorPos()
    OS-->>Main: cursor Point
    Main->>Neko: tick(cursor)
    Neko->>Neko: calc direction angle
    Neko->>Neko: advance state machine
    Neko->>Neko: move position toward cursor
    Neko-->>Main: (state, frame_name, x, y)
    Main->>Pet: update(state, frame_name, x, y)
    Pet->>Pet: swap PhotoImage on canvas
    Main->>Main: root.after(fps, tick)
```

## State Transition (idle path)

```mermaid
sequenceDiagram
    participant Neko
    Note over Neko: cursor stops moving
    Neko->>Neko: STOP (count ticks up to stop_time)
    Neko->>Neko: WASH (count up to wash_time)
    Neko->>Neko: SCRATCH (count up to scratch_time)
    Neko->>Neko: YAWN (count up to yawn_time)
    Neko->>Neko: SLEEP (loop until cursor moves)
    Note over Neko: cursor moves
    Neko->>Neko: AWAKE (brief wake animation)
    Neko->>Neko: *_MOVE toward cursor
```

## Development Workflow

```
poetry install          # install all deps including dev
poetry run python -m neko2020  # run from source
pre-commit install      # wire up black + flake8 hooks
poetry run pytest       # run tests
poetry run pyinstaller neko2020.spec  # build dist/neko2020.exe
```

## Adding a New Animal Type

1. Create `resource/<animal_name>/` directory
2. Add all 32 `.ico` files named exactly as the hard-coded list in `utils/images.py`
3. Set `animal: <animal_name>` in `~/.config/neko2020/config.yml`, or use `"random"` to include it in rotation
