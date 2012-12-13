========
Scandium
========

Installation
============

Scandium depends on:

 - twisted
 - flask
 - qt4reactor
 - PySide
 - py2exe

The most hassle-free installation method is to download and install twisted, PySide and py2exe separately. Setuptools will take care of the other dependencies.

Creating a Project
==================

Running ``scadmin.py startproject projectname`` will produce the following in the current directory:::

 - scandium-projectname
 | - runapp.py
 | - setup.py
 \ - projectname
   | - __init__.py
   | - settings.py
   | - static
   | | - css
   | | - icons
   | \ - js
   | - templates
   |  \ - index.html
   \ views.py

Getting Started
===============

If you've got your dependencies in order, ``python runapp.py`` will generate a Scandium 'hello world' application from a blank project. 

Add views, templates and static content in the obvious places.

Configuration
-------------

You can override the default configuration by modifying ``settings.py``. Available settings and defaults are as follows:

DEBUG 
^^^^^

Debug flag for the Scandium app. Enables 

Default: ``True``


FLASK_DEBUG
^^^^^^^^^^^

Sets the debug flag on the Flask app. Enables in-browser tracebacks etc.

Default: ``True``

HTTP_PORT
^^^^^^^^^

Port to listen for HTTP connections.

Default: ``8080``

STATIC_RESOURCE
^^^^^^^^^^^^^^^

Defines where to find static resources. Can be a filepath or a tuple of (package, directoryname). You must use the latter format if you want to deploy your application using a compressed or bundled distributable.
The default value for this setting is defined in settings.py because the project name is required.

Default: ``(projectname, 'static')``

TEMPLATE_RESOURCE
^^^^^^^^^^^^^

Defines where to find templates. Can be a filepath or a tuple of (package, directoryname). You must use the latter format if you want to deploy your application using a compressed or bundled distributable.
The default value for this setting is defined in settings.py because the project name is required.

Default: ``(projectname, 'templates')``

ALLOW_DEFERREDS
^^^^^^^^^^^^^^^

If enabled, views may return twisted deferred objects. The response will be returned to the browser when the deferred fires.

Default: ``False``


ICON_RESOURCE
^^^^^^^^^^^^^

Defines the image to use for the application icon. Can be a filepath or a tuple of (package, directoryname). You must use the latter format if you want to deploy your application using a compressed or bundled distributable.

Default: None

WINDOW_TITLE
^^^^^^^^^^^^

Title to be displayed in the browser window. Adding a ``<title></title>`` tag to your HTML page won't affect this.

Default: ``"Scandium Browser"``

WINDOW_GEOMETRY
^^^^^^^^^^^^^^^

Size and position for the application window, specified as ``(x, y, width, height)``.

Default: ``(100, 100, 800, 500)``


Custom Settings
---------------

It is possible to define custom settings in ``settings.py`` for use in your web application code. Just do ``from projectname import sc`` and reference the settings using ``sc.conf.SETTING_NAME``.


Building with py2exe
====================

TODO
