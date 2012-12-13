import os
import sys
import fnmatch
from setuptools import setup, find_packages

import scandium


def find_package_data(package, *paths):
    data = {package: []}
    for path in paths:
        for root, _, filenames in os.walk(os.path.join(package, path)):
            for filename in filenames:
                pkg_path = os.path.join(os.path.relpath(root, package))
                data[package].append(pkg_path, filename)
    return data
    
NAME = "scandium"
VERSION = scandium.__version__
INCLUDES = ['twisted.web.resource', 'jinja2.ext', 'PySide.QtNetwork']
PACKAGES = find_packages(exclude="tests")
PACKAGE_DATA_DIRS = ('static', 'templates')
PACKAGE_DATA = find_package_data((NAME,) + PACKAGE_DATA_DIRS)

AUTHOR = "Matt Bennett"
EMAIL = "matt.bennett@inmarsat.com"
KEYWORDS = "scandium web desktop application"
DESCRIPTION = "A toolkit for transformation webapps into "\
              "desktop applications under QtWebKit."
LICENSE = "BSD"
LONG_DESC = open(os.path.join(os.path.dirname(__file__), 'README')).read()

extra_cfg = {}

if 'py2exe' in sys.argv:
    import py2exe
    from py2exe.build_exe import py2exe as build_exe
    from distutils.sysconfig import get_python_lib

    #embedding package_data in py2exe's distributable
    #see: http://crazedmonkey.com/blog/python/pkg_resources-with-py2exe.html
    class MediaCollector(build_exe):
        def copy_extensions(self, extensions):
            build_exe.copy_extensions(self, extensions)
            
            def collect_from(path):
                for root, _, filenames in os.walk(path):
                    for fname in fnmatch.filter(filenames, '*'):
                        parent = os.path.join(self.collect_dir, root)
                        if not os.path.exists(parent):
                            self.mkpath(parent)
                        self.copy_file(os.path.join(root, fname), \
                                       os.path.join(parent, fname))
                        self.compiled_files.append(os.path.join(root, fname))
            for dname in PACKAGE_DATA_DIRS:
                collect_from(os.path.join(NAME, dname))
                collect_from(os.path.join(NAME, dname))
    
    path = os.path.join(get_python_lib(), 'PySide', 'plugins', 'imageformats')
    imageformats = []
    for dll in os.listdir(path):
        imageformats.append(os.path.join(path, dll))
    
    path = os.path.join(get_python_lib(), 'PySide')
    qt = []
    for dll in ("QtCore4.dll", "QtGui4.dll", "QtNetwork4.dll"):
        qt.append(os.path.join(path, dll))
    
    extra_cfg.update({
        'cmdclass': {'py2exe': MediaCollector},
        'console': [{
            'script': '%s/config/run.py' % NAME,
            'icon_resources': [(1, '%s/static/icons/icon.ico' % NAME)]
        }],
        'zipfile': None,
        'data_files': [('imageformats', imageformats), ('', qt)]
    })



setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = EMAIL,
    description = DESCRIPTION,
    license = LICENSE,
    keywords = KEYWORDS,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    options = {
        "py2exe": {
            "compressed": 1,
            "optimize": 1,
            "ascii": 0,
            "bundle_files": 1,
            "packages": PACKAGES,
            "includes": INCLUDES,
            'dll_excludes': ['w9xpopen.exe']
        }
    },
    long_description=LONG_DESC,
    classifiers=[
        #
    ],
    dependency_links = [
        "https://github.com/ghtdak/qtreactor/tarball/master#egg-qt4reactor-1.0"
    ],
    scripts = ['bin/scadmin.py'],
    install_requires=[
        "twisted",
        "qt4reactor",
        "flask",
        "PySide", #best to install this manually - pip isn't so hot at it
    ],
    **extra_cfg
)