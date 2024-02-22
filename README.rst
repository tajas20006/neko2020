Neko2020
========

Neko2020 a reimagining of oneko for Windows implemented in Python.

If you are interested in the history of oneko you can read an interesting shortread from https://github.com/eliot-akira/neko.
Thanks to this article it was possible to find an additional icon library, which was implemented in this project.

Running Neko
-------------------
Windows
___________________
Download the project using ``git clone``. 
Create a file %USERPROFILE%\.config\neko2020\config.yml and copy the contents of ``default_config.yml`` into it.
Run neko2020.exe

Linux
-------------------

This project is primarily oriented for Windows.
For Linux, we recommend to read the oneko original or the source code below.

Configuring
-------------------

With config.yml you can customize the characteristics of your pet. To change the pet you need to change the value of the animal key to the name of any catalog from the resource directory.

You can extend the pet bibliotheca by adding your own icons to the resource catalog. The name of the subdirectory will become the name of the pet. The files must be in .ico format. The default scale is 32x32, but you can be whatever you want. Don't forget to rename the icons similarly to other pets.

Source and Building
------------------

Supported version of ``Python 3.8``
neko2020 uses the poetry dependency manager.

Run the dependency installation in the project folder with the poetry install command ``poetry install``

To start Neko2020 run ``poetry run python -m neko2020``
(or ``path/to/neko2020/.venv/Scripts/python -m neko2020`` to run from other directories.)

Whether you have made changes to the code or just decided to rebuild the file again run poetry run pyinstaller neko2020.spec and a new neko2020.exe will be created in the dist folder.
``poetry run pyinstaller neko2020.spec``

For work on Linux, copy file ``cp config\default_config.yml $XDG_CONFIG_HOME/neko2020/config.yml``.
If ``XDG_CONFIG_HOME`` is not set, it will default to ``$HOME/.config``.

For rebuilding the binary i use pyinstaller to build the binary.

Stopping Neko
-------------

There is an icon in the system tray.
Just right click and click "Quit".

TODOs
-----
- Does not work for dual displays.  Neko will run only in the main display.
