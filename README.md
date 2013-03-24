gcs
====

gcs is a cross-platform GCODE debug/step and alignment tool for Grbl like GCODE interpreter.
with features similar to software debugger. For example usage of breakpoints, change program
counter (position), stop and inspection/modification of machine variables, step, run.

use case: The GCODE file is a drill program for a PCB, gcs will make it possible to set-up a
break point right before the tool plunge. At this point with the jogging controls it is possible
to lower the tool right before penetrating the surface to verify alignment is adequate. Once
this is verify and or adjusted, the program can continue.

Development Environment
---------------------
### gcs's dependencies are:
* [python 2.7] (http://www.python.org)
* [pySerial 2.5](http://pyserial.sourceforge.net/)
* [wxPython 2.8](http://www.wxpython.org/)

### Additional dependencies if enabling Computer Vision
* [OpenCV 2.4.1] (http://opencv.org/)
* [numpy 1.6.1] (http://pypi.python.org/pypi/numpy)

NOTE: As of this writing in Windows OS OpenCV 2.4.1. doesn't work well with Python 64bit, please use python 32bit.

### Devices
* [Grbl 0.8c] (http://github.com/grbl/grbl/blob/master/README.md)
* [ShapeOko] (http://www.shapeoko.com/)

### OSes:
* [Ubuntu 12.04 (32/64)] (http://www.ubuntu.com/)
* Windows 7 (32/64)

### Editors
* [Geany] (http://www.geany.org/)
* [Notepad ++] (http://notepad-plus-plus.org/)

Screen Shoots
------------
![Main window, stop on a breakpoint](https://github.com/duembeg/gcs/raw/master/images/screenshoot/main_window.png "Main window, stop on a breakpoint")
![Settings Dialog](https://github.com/duembeg/gcs/raw/master/images/screenshoot/settings_dialog.png "Settings Dialog")
![About Dialog](https://github.com/duembeg/gcs/raw/master/images/screenshoot/about_box.png "About Dialog")

Changelog
---------
1.1.0
* UI updates
   * Added Find and Goto Line controls to tool bar.
   * Added G-Code syntax highlighting.
   * Updated icons to more colorful versions.
   * Removed CLI panel, moved CLI into Jogging panel.
* Separated code into modules, for better maintainability and preparing for plug-in support.

1.0.0
* Initial Release
