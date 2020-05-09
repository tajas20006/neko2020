Neko2020
========

Neko2020 is a reinvenstion of Neko for Windows implemented with Python.

For more information and history about Neko, please refer to `this article`_ in Wikipedia.

.. _this article: https://en.wikipedia.org/wiki/Neko_(software)


Running Neko
------------

For Windows, there is a prebuilt binary ``neko2020.exe``.

For Linux, I recommend you try out `the official version`_ which you can install with ``sudo apt install oneko``.

.. _the official version: http://www.daidouji.com/oneko/


Running from source
-------------------

If you have poetry installed: ``poetry install``

If you do not have poetry, you can use pip to install the dependencies:
``pip install pyautogui infi.systray pyyaml``

To start Neko2020, run ``poetry run python -m neko2020``
(or ``path/to/neko2020/.venv/Scripts/python -m neko2020`` to run from other directories.)


Configuring Neko
----------------

Partially implemented.

Create ``$XDG_CONFIG_HOME/neko2020/config.yml`` and edit the file.
If XDG_CONFIG_HOME is not set, it will default to ``$HOME/.config``.

All the supported configs are listed in the ``config/default_config.yml``.
Anything you write in your config.yml will override the default_config.yml.

If you want your Neko to be something other than a cat, you can place your icons in resource directory.
The name of the subdirectory becomes the name of the pet, which you can specify in your config file.


Stopping Neko
-------------

There is an icon in the system tray.
Just right click and click "Quit".


Rebuilding the binary
---------------------

I use pyinstaller to build the binary.

``poetry run pyinstaller neko2020.spec``


TODOs
-----
- Does not work for dual displays.  Neko will run only in the main display.
