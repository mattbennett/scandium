from PySide import QtGui
app = QtGui.QApplication([])
import qt4reactor
qt4reactor.install()

__version__ = "0.0.0"


def Scandium(*args, **kwargs):
    from .core import Harness
    return Harness(*args, **kwargs)