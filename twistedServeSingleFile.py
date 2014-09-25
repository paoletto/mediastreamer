import warnings
import string
import types
import copy
import os
from urllib import quote

from zope.interface import implements

from urllib import unquote



from twisted.web.server import Site, Request, Session
from twisted.web.static import File
from twisted.internet import reactor
from twisted.web.http import HTTPFactory, HTTPChannel
from twisted.web import util as webutil, resource as webresource


class MyHTTPChannel(HTTPChannel):
    def __init__(self):
        HTTPChannel.__init__(self)


    def connectionLost(self, reason):
        print "connectionLost in MyHTTPChannel. channel is ", self
        HTTPChannel.connectionLost(self,reason)


    def connectionMade(self):
        print "connectionMade in MyHTTPChannel"
        HTTPChannel.connectionMade(self)


class MyHTTPFactory(HTTPFactory):
    protocol = MyHTTPChannel
    def __init__(self, logPath=None, timeout=60*60*12):
        HTTPFactory.__init__(self, logPath,timeout)

class MySite(MyHTTPFactory):
    """
    A web site: manage log, sessions, and resources.

    @ivar counter: increment value used for generating unique sessions ID.
    @ivar requestFactory: factory creating requests objects. Default to
        L{Request}.
    @ivar displayTracebacks: if set, Twisted internal errors are displayed on
        rendered pages. Default to C{True}.
    @ivar sessionFactory: factory for sessions objects. Default to L{Session}.
    @ivar sessionCheckTime: Deprecated.  See L{Session.sessionTimeout} instead.
    """
    counter = 0
    requestFactory = Request
    displayTracebacks = True
    sessionFactory = Session
    sessionCheckTime = 1800

    def __init__(self, resource, logPath=None, timeout=60*60*12):
        """
        Initialize.
        """
        MyHTTPFactory.__init__(self, logPath=logPath, timeout=timeout)
        self.sessions = {}
        self.resource = resource

    def _openLogFile(self, path):
        from twisted.python import logfile
        return logfile.LogFile(os.path.basename(path), os.path.dirname(path))

    def __getstate__(self):
        d = self.__dict__.copy()
        d['sessions'] = {}
        return d

    def _mkuid(self):
        """
        (internal) Generate an opaque, unique ID for a user's session.
        """
        from twisted.python.hashlib import md5
        import random
        self.counter = self.counter + 1
        return md5("%s_%s" % (str(random.random()) , str(self.counter))).hexdigest()

    def makeSession(self):
        """
        Generate a new Session instance, and store it for future reference.
        """
        uid = self._mkuid()
        session = self.sessions[uid] = self.sessionFactory(self, uid)
        session.startCheckingExpiration()
        return session

    def getSession(self, uid):
        """
        Get a previously generated session, by its unique ID.
        This raises a KeyError if the session is not found.
        """
        return self.sessions[uid]

    def buildProtocol(self, addr):
        """
        Generate a channel attached to this site.
        """
        channel = MyHTTPFactory.buildProtocol(self, addr)
        channel.requestFactory = self.requestFactory
        channel.site = self
        return channel

    isLeaf = 0

    def render(self, request):
        """
        Redirect because a Site is always a directory.
        """
        request.redirect(request.prePathURL() + '/')
        request.finish()

    def getChildWithDefault(self, pathEl, request):
        """
        Emulate a resource's getChild method.
        """
        request.site = self
        return self.resource.getChildWithDefault(pathEl, request)

    def getResourceFor(self, request):
        """
        Get a resource for a request.

        This iterates through the resource heirarchy, calling
        getChildWithDefault on each resource it finds for a path element,
        stopping when it hits an element where isLeaf is true.
        """
        request.site = self
        # Sitepath is used to determine cookie names between distributed
        # servers and disconnected sites.
        request.sitepath = copy.copy(request.prepath)
        return webresource.getChildForRequest(self.resource, request)

class MyFile(File):
    def __init__(self, path, defaultType="text/html", ignoredExts=(), registry=None, allowExt=0):
        File.__init__(self,path, defaultType,ignoredExts,registry,allowExt)


    def echoFunction(fn):
        "Returns a traced version of the input function."
        from itertools import chain
        def wrapped(*v, **k):
            name = fn.__name__
            print "%s(%s)" % (
                name, ", ".join(map(repr, chain(v, k.values()))))
            return fn(*v, **k)
        return wrapped

    # def ignoreExt(self, ext):
    #     return File.ignoredExts(self, ext)
    #
    # def directoryListing(self):
    #     return File.directoryListing()
    #
    # def getChild(self, path, request):
    #     return File.getChild(self,path,request)
    #
    # def openForReading(self):
    #     return File.openForReading(self)
    #
    # def getFileSize(self):
    #     return File.getFileSize(self)
    #
    # def _parseRangeHeader(self, range):
    #     return File._parseRangeHeader(self, range)
    #
    # def _rangeToOffsetAndSize(self, start, end):
    #     return File._rangeToOffsetAndSize(self, start, end)
    #
    # def _contentRange(self, offset, size):
    #     return File._contentRange(self, offset, size)
    #
    # def _doSingleRangeRequest(self, request, (start, end)):
    #     return File._doSingleRangeRequest(self, request, (start, end))
    #
    # def _doMultipleRangeRequest(self, request, byteRanges):
    #     return File._doMultipleRangeRequest(self, request, byteRanges)
    #
    # def _setContentHeaders(self, request, size=None ):
    #     return File._setContentHeaders(self, request, size)
    #
    # def makeProducer(self, request, fileForReading):
    #     return File.makeProducer(self, request, fileForReading)
    #
    def render_GET(self, request):
        # set up the transcoding to a named pipe
        # store the pid of the transcoding process in a map
        print "render_GET: channel is ", request.channel
        # create a producer, and pass the name of the pipe

        return File.render_GET(self, request)
    #
    # def redirect(self, request):
    #     return File.redirect(self, request)
    #
    # def listNames(self):
    #     return File.listEntities(self)
    #
    # def listEntities(self):
    #     return File.listEntities(self)
    #
    # def createSimilarFile(self, path):
    #     return File.createSimilarFile(self, path)


    # ignoreExt = echoFunction(File.ignoreExt)
    #
    # directoryListing = echoFunction(File.directoryListing)
    #
    # getChild = echoFunction(File.getChild)
    #
    openForReading = echoFunction(File.openForReading)
    #
    # getFileSize = echoFunction(File.getFileSize)

    _parseRangeHeader = echoFunction(File._parseRangeHeader)

    # _rangeToOffsetAndSize = echoFunction(File._rangeToOffsetAndSize)
    #
    # _contentRange = echoFunction(File._contentRange)
    #
    # _doSingleRangeRequest = echoFunction(File._doSingleRangeRequest)
    #
    # _doMultipleRangeRequest = echoFunction(File._doMultipleRangeRequest)
    #
    # _setContentHeaders = echoFunction(File._setContentHeaders)
    #
    # makeProducer = echoFunction(File.makeProducer)
    #
    #render_GET = echoFunction(File.render_GET)
    #
    # redirect = echoFunction(File.redirect)
    #
    # listNames = echoFunction(File.listNames)
    #
    # listEntities = echoFunction(File.listEntities)
    #
    # createSimilarFile = echoFunction(File.createSimilarFile)



resource = MyFile('D:/temp/streaming', defaultType='video/octet-stream')
factory = MySite(resource)
reactor.listenTCP(8000, factory)
reactor.run()