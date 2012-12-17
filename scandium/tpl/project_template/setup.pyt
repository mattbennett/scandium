from setuptools import setup, find_packages
from py2exe.build_exe import py2exe as build_exe
from distutils.sysconfig import get_python_lib
import fnmatch
import py2exe
import sys
import os

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

################################################################
# Customize these variables

NAME = "{{project_name}}"
VERSION = "{{version}}"
DESCRIPTION = "{{description}}"
COMPANY_NAME = "{{company_name}}"
LICENSE = "{{license}}"

# Fiddle with these variables if you use Python modules that
# py2exe can't find, or you change the location of static
# and template data.

INCLUDES = ['jinja2.ext', 'PySide.QtNetwork']
EXCLUDES = ["Tkconstants", "Tkinter", "tcl"]
PACKAGES = find_packages(exclude=("tests",))
PACKAGE_DATA_DIRS = ('static', 'templates')


################################################################
# A program using PySide

# The manifest will be inserted as resource into {{project_name}}.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-) and
# ensures the Visual C++ Redistributable Package DLLs get found.
#
# Another option would be to store it in a file named
# {{project_name}}.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="{{project_name}}"
    type="win32"
/>
<description>{{project_name}} Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="X86"
            publicKeyToken="1fc8b3b9a1e18e3b"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24


# Extention to embed package_data in py2exe's distributable
# See: http://crazedmonkey.com/blog/python/pkg_resources-with-py2exe.html
class MediaCollector(build_exe):
    def copy_extensions(self, extensions):
        build_exe.copy_extensions(self, extensions)
        
        def collect_media(path):
            for root, _, filenames in os.walk(path):
                for fname in fnmatch.filter(filenames, '*'):
                    parent = os.path.join(self.collect_dir, root)
                    if not os.path.exists(parent):
                        self.mkpath(parent)
                    self.copy_file(os.path.join(root, fname), \
                                   os.path.join(parent, fname))
                    self.compiled_files.append(os.path.join(root, fname))
        for dname in PACKAGE_DATA_DIRS:
            collect_media(os.path.join(NAME, dname))
            collect_media(os.path.join(NAME, dname))


# Create Windows Application target
# 
class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = VERSION
        self.company_name = COMPANY_NAME
        self.description = DESCRIPTION
        self.copyright = LICENSE
        self.name = NAME

app = Target(
    # what to build
    script = "runapp.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog=NAME))],
    icon_resources = [(1, "%s/static/icons/icon.ico" % NAME)],
    dest_base = NAME
)


# Qt4 uses plugins for image processing. These cannot be bundled into the
# executable, so we copy them into the application directory, along with
# the Qt DLL files, which we then exclude from the bundle.
path = os.path.join(get_python_lib(), 'PySide', 'plugins', 'imageformats')
imageformats = []
for dll in os.listdir(path):
    imageformats.append(os.path.join(path, dll))

path = os.path.join(get_python_lib(), 'PySide')
qt = []
for dll in ("QtCore4.dll", "QtGui4.dll", "QtNetwork4.dll"):
    qt.append(os.path.join(path, dll))

DATA_FILES = [('imageformats', imageformats), ('', qt)]
    
    
################################################################

setup(
    cmdclass = {'py2exe': MediaCollector},
    data_files = DATA_FILES,
    include_package_data=True,
    options = {"py2exe": {"compressed": 1,
                          "optimize": 1,
                          "ascii": 0,
                          "bundle_files": 1,
                          "packages": PACKAGES,
                          "includes": INCLUDES,
                          "excludes": EXCLUDES,
                          # exclude the Qt4 DLLs to ensure the data_files version gets used, otherwise image processing will fail
                          "dll_excludes": ['msvcp90.dll', 'w9xpopen.exe', "QtCore4.dll", "QtGui4.dll", "QtNetwork4.dll"]}},
    zipfile = None,
    windows = [app],
)