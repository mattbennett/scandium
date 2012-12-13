from twisted.internet import reactor, defer
from twisted.python.failure import Failure
from twisted.web import server, resource
from twisted.web.wsgi import WSGIResource

from werkzeug.wsgi import SharedDataMiddleware
from jinja2.loaders import FileSystemLoader, PackageLoader
from flask import Flask

from PySide import QtGui
from PySide.QtWebKit import QWebView, QWebSettings
from PySide.QtCore import QUrl, QByteArray

import pkgutil


# See http://stackoverflow.com/questions/6690639/how-to-configure-static-serving-in-twisted-with-django
class SharedRoot(resource.Resource):
    "Root resource that combines the two sites/entry points"
    WSGI = None

    def getChild(self, child, request):
        request.prepath.pop()
        request.postpath.insert(0, child)
        return self.WSGI

    def render(self, request):
        return self.WSGI.render(request)
    
    
class Browser(QWebView):
    "Web browser"
    def __init__(self, url, title=None, geometry=None, icon=None):
        super(Browser, self).__init__()
        
        self.setGeometry(*geometry)
        self.setWindowTitle(title)
        
        if icon:
            pixmap = QtGui.QPixmap()
            if type(icon) == tuple:  # package, not file path
                img_data = pkgutil.get_data(*icon)
            else:
                with open(icon) as fh:
                    img_data = fh.read()
            pixmap.loadFromData(QByteArray(img_data))
            self.setWindowIcon(QtGui.QIcon(pixmap))

        self.load(QUrl(url))
        
    def closeEvent(self, event):
        event.accept()
        reactor.stop()


class Config(object):
    """
    Scandium Config object, handles configuration defaults and customization.
    """
    DEBUG = True
    FLASK_DEBUG = True
    HTTP_PORT = 8080
    STATIC_ROOT = 'static'
    TEMPLATE_ROOT = 'templates'
    ALLOW_DEFERREDS = True
    ICON_RESOURCE = None
    WINDOW_TITLE = "Scandium Browser"
    WINDOW_GEOMETRY = (100, 100, 800, 500)
    
    def update(self, settings_module):
        for setting in dir(settings_module):
            if setting == setting.upper():
                setattr(self, setting, getattr(settings_module, setting))


class Harness():
    """
    Main Scandium object
    """
    def __init__(self):
        self.conf = Config()
        
    def start(self):
        root = SharedRoot()
        root.WSGI = WSGIResource(reactor, reactor.getThreadPool(), self.app)
        self.webserver = server.Site(root)
        
        reactor.listenTCP(self.conf.HTTP_PORT, self.webserver)
        reactor.callLater(0, self.browser.show)
        reactor.run()
    
    @property
    def app(self):
        if not hasattr(self, '_app'):
            self._app = self._create_app()
        return self._app
    
    @property
    def browser(self):
        if not hasattr(self, '_browser'):
            self._browser = self._create_browser()
        return self._browser
    
    def _create_app(self):
        app = Flask(__name__)
        app.debug = self.conf.FLASK_DEBUG
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/': self.conf.STATIC_ROOT
        })
        if type(self.conf.TEMPLATE_ROOT) == tuple:  # package, not file path
            app.jinja_loader = PackageLoader(*self.conf.TEMPLATE_ROOT)
        else:
            app.jinja_loader = FileSystemLoader(self.conf.TEMPLATE_ROOT)
        if self.conf.ALLOW_DEFERREDS:
            self._enable_deferreds(app)
        return app
    
    def _create_browser(self):
        browser = Browser('http://localhost:%d/' % self.conf.HTTP_PORT, \
                          icon=self.conf.ICON_RESOURCE,
                          title=self.conf.WINDOW_TITLE,
                          geometry=self.conf.WINDOW_GEOMETRY)
        
        devextras = QWebSettings.WebAttribute.DeveloperExtrasEnabled
        browser.settings().setAttribute(devextras, self.conf.DEBUG)
        return browser

    def _enable_deferreds(self, app):
            import Queue
            import functools
        
            #From the comments here:
            #http://www.saltycrane.com/blog/2008/10/cant-block-deferred-twisted
            def block_on(d):
                "Block until a deferred fires"
                q = Queue.Queue()
                d.addBoth(q.put)
                ret = q.get()
                if isinstance(ret, Failure):
                    ret.raiseException()
                else:
                    return ret
            
            def routeMaybeDeferred(rule, **options):
                """
                A routing method that allows the view function to return a
                deferred, and if so blocks for it to complete.
                
                This is a hack: we should really be using something like
                https://github.com/twisted/klein, but klein won't work with the
                Qt reactor.
                """
                def decorator(f):
                    blocking = lambda func=None, *args, **kw: \
                        block_on(defer.maybeDeferred(func, *args, **kw))
                    fn = functools.partial(blocking, func=f)
                    fn.__name__ = f.__name__  # partials don't inherit __name__
                    endpoint = options.pop('endpoint', None)
                    app.add_url_rule(rule, endpoint, fn, **options)
                    return fn
                return decorator
            app.route = routeMaybeDeferred
