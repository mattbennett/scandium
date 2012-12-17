import os
from setuptools import setup, find_packages


def find_package_data(package, *paths):
    data = {package: []}
    for path in paths:
        for root, _, filenames in os.walk(os.path.join(package, path)):
            for fname in filenames:
                pkg_path = os.path.join(os.path.relpath(root, package), fname)
                data[package].append(pkg_path)
    return data
    
NAME = "scandium"
VERSION = '0.0.1'
PACKAGES = find_packages(exclude="tests")
PACKAGE_DATA_DIRS = ('tpl',)
PACKAGE_DATA = find_package_data(NAME, *PACKAGE_DATA_DIRS)

AUTHOR = "Matt Bennett"
EMAIL = "matt.bennett@inmarsat.com"
KEYWORDS = "scandium web desktop application titanium"
DESCRIPTION = "Titanium Desktop replacement. A toolkit for transformation of" \
              " python webapps into desktop applications under QtWebKit."
LICENSE = "BSD"


setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = EMAIL,
    description = DESCRIPTION,
    license = LICENSE,
    keywords = KEYWORDS,
    packages = PACKAGES,
    package_data = PACKAGE_DATA,
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        #
    ],
    dependency_links = [
        # setuptools will install from list link, but do so as a zipped egg.
        # py2exe can't import qt4reactor from a zip, so building your scandium
        # into an exe will fail. Installing qt4reactor manually is recommended.
        #"https://github.com/ghtdak/qtreactor/zipball/master#egg=qt4reactor-1.0"
    ],
    scripts = ['bin/scadmin.py'],
    install_requires = [
        "twisted",              # manual install recommended
        "qt4reactor>=1.0",      # manual install recommended
        "flask",
        "PySide",               # manual install recommended
    ]
)