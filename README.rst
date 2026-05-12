Neko2020
========

Neko2020 a reimagining of oneko for Windows implemented in Python.

If you are interested in the history of oneko you can read an interesting shortread from https://github.com/eliot-akira/neko.
Thanks to this article it was possible to find an additional icon library, which was implemented in this project.

Windows
-------------------
Download the project using ``git clone``, or grab the latest ``neko2020.exe``
from the `Releases <https://github.com/tajas20006/neko2020/releases>`_ page.

Run ``neko2020.exe``. A system tray icon will appear; right-click it to
configure, start, stop, restart, or quit the application.

A user config file is automatically loaded from
``%USERPROFILE%\.config\neko2020\config.yml`` if it exists.  To customise
settings, open the **Config** dialog from the tray menu — it writes the file
for you.

Linux
-------------------

This project is primarily oriented for Windows.
For Linux, we recommend to read the oneko original or the source code below.

Configuring
-------------------

The easiest way to configure neko2020 is through the **Config** dialog in the
system tray.  It lets you adjust the animal sprite, movement speed, behavior
timing, and animation rate without editing files manually.

Alternatively you can create ``~/.config/neko2020/config.yml`` (or
``%XDG_CONFIG_HOME%\neko2020\config.yml`` on Windows) and set only the keys
you want to override — the file is deep-merged over the built-in defaults.

Key configuration options:

- ``animal`` — name of any subdirectory under ``resource/``, or ``"random"``
  to pick a different sprite set each run.
- ``speed.max`` / ``speed.min`` — pixels per frame the pet can travel.
- ``fps`` — animation frame rate (frames per second).
- ``duration.*`` — number of animation cycles spent in each idle action.
- ``offset.x`` / ``offset.y`` — pixel offset of the sprite relative to the
  cursor.

You can extend the pet library by adding your own sprite sets.  Place a
subdirectory containing 32 ``.ico`` files either in the ``resource/`` folder
(next to the executable) or in ``~/.config/neko2020/resources/<name>/``.
The subdirectory name becomes the animal name.  File names must exactly match
those used by the built-in sets.

Source and Building
------------------

Supported Python versions: ``3.12`` to ``3.13``.

neko2020 uses the `uv <https://github.com/astral-sh/uv>`_ package manager.

Install dependencies::

    uv sync

Run from source::

    uv run python -m neko2020

Build the standalone executable::

    uv run pyinstaller neko2020.spec

The executable will be created at ``dist/neko2020.exe``.

For work on Linux, copy the default config::

    cp config/default_config.yml $XDG_CONFIG_HOME/neko2020/config.yml

If ``XDG_CONFIG_HOME`` is not set, it defaults to ``$HOME/.config``.

Stopping Neko
-------------

There is an icon in the system tray.
Just right click and click "Quit".

Even If you started neko from cmd/bash, DO NOT use ctrl+c to stop neko.
Console may go unresponsive.

Other Commands
-------------

- Config

  Opens a GUI dialog to adjust all settings. Changes are saved to your user
  config and take effect immediately (the pet restarts briefly).

- Start / Stop

  Use these to show / hide neko.

- Restart

  Reloads the config and restarts the animation.
