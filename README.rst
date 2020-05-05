Neko2020
========

Neko2020 is a reinvenstion of Neko for Windows implemented with Python.

For more information and history about Neko, please refer to `this article`_ in Wikipedia.

.. _this article: https://en.wikipedia.org/wiki/Neko_(software)

Installation
------------
If you have poetry installed: ``poetry install``

If you do not have poetry, you can use pip to install the dependencies:
``pip install pyautogui infi.systray pyyaml``

To start Neko2020, run ``poetry run python -m neko2020``
(or ``path/to/neko2020/.venv/Scripts/python -m neko2020`` to run from other directories.)

Configuring Neko
----------------

Partially implemented.

For now, can modify ``config/default_config.yml`` directly, and you will see the changes.

You can configure Neko using a yaml file.
The default configuration is saved in ``config/default_config.yml``.
You can change any one of the option to change speed, size, and so on.

If you want your Neko to be something other than a cat, you can place your icons in resource directory.
The name of the subdirectory becomes the name of the pet, which you can specify in your config file.

Stopping Neko
-------------

There is an icon in the system tray.
Just right click and click "Quit".

TODOs
-----
- Neko will not respect config files yet.
  Everything is hard coded for now.
- Does not work for dual displays.  Neko will run only in the main display.
