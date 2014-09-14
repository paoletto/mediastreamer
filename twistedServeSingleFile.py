from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor


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
    # def render_GET(self, request):
    #     return File.render_GET(self, request)
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
    # openForReading = echoFunction(File.openForReading)
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
    # render_GET = echoFunction(File.render_GET)
    #
    # redirect = echoFunction(File.redirect)
    #
    # listNames = echoFunction(File.listNames)
    #
    # listEntities = echoFunction(File.listEntities)
    #
    # createSimilarFile = echoFunction(File.createSimilarFile)



resource = MyFile('D:/temp', defaultType='video/octet-stream')
factory = Site(resource)
reactor.listenTCP(8000, factory)
reactor.run()