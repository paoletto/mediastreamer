import warnings
import string
import types
import copy
import os
from urllib import quote

from zope.interface import implements
from twisted.internet import abstract, interfaces
from urllib import unquote


from twisted.web.server import Site, Request, Session
import twisted.web as tw
import twisted.python
from twisted.web.static import File
from twisted.internet import reactor
from twisted.web.http import HTTPFactory, HTTPChannel
from twisted.web import util as webutil, resource as webresource
import mkvgenerator


#sDataBasedir = "D:/temp/streaming/TESTS/"
sDataBasedir = "BBBEXAMPLE/"
#sMovieName = "myH264testMovie"
sMovieName = "BBB_ffmpeg_360p_crf30"
sMoviePath = sDataBasedir + sMovieName + ".mkv"
sHeaderPath = sDataBasedir + sMovieName + "_headerOnly.mkv"
sDataPath   = sDataBasedir + sMovieName + "_dataOnly.mkv"
sCuesPath   = sDataBasedir + sMovieName + "_cuesOnly.mkv"
#sSeekheadPath   = sDataBasedir + sMovieName + "_seekheadOnly.mkv"



def fillExampleClusterOffsets():
    clusterOffsets = list()
    clusterOffsets.append( 1330 )
    clusterOffsets.append( 143325 )
    clusterOffsets.append( 437808 )
    clusterOffsets.append( 746473 )
    clusterOffsets.append( 1051747 )
    clusterOffsets.append( 1332299 )
    clusterOffsets.append( 1573728 )
    clusterOffsets.append( 1881678 )
    clusterOffsets.append( 2119364 )
    clusterOffsets.append( 2384144 )
    clusterOffsets.append( 2535540 )
    clusterOffsets.append( 2900143 )
    clusterOffsets.append( 3099470 )
    clusterOffsets.append( 3300387 )
    clusterOffsets.append( 3490715 )
    clusterOffsets.append( 3716377 )
    clusterOffsets.append( 3908308 )
    clusterOffsets.append( 4143973 )
    clusterOffsets.append( 4375372 )
    clusterOffsets.append( 4631876 )
    clusterOffsets.append( 4823820 )
    clusterOffsets.append( 5108436 )
    clusterOffsets.append( 5270121 )
    clusterOffsets.append( 5474213 )
    clusterOffsets.append( 5680428 )
    clusterOffsets.append( 5899730 )
    clusterOffsets.append( 6112982 )
    clusterOffsets.append( 6316254 )
    clusterOffsets.append( 6540625 )
    clusterOffsets.append( 6715400 )
    clusterOffsets.append( 6855836 )
    clusterOffsets.append( 7196234 )
    clusterOffsets.append( 7384367 )
    clusterOffsets.append( 7534524 )
    clusterOffsets.append( 7728357 )
    clusterOffsets.append( 7886048 )
    clusterOffsets.append( 8317486 )
    clusterOffsets.append( 8493652 )
    clusterOffsets.append( 8675165 )
    clusterOffsets.append( 8893322 )
    clusterOffsets.append( 9053778 )
    clusterOffsets.append( 9300282 )
    clusterOffsets.append( 9543879 )
    clusterOffsets.append( 9722535 )
    clusterOffsets.append( 9935550 )
    clusterOffsets.append( 10068834 )
    clusterOffsets.append( 10291716 )
    clusterOffsets.append( 10565908 )
    clusterOffsets.append( 10802939 )
    clusterOffsets.append( 11061065 )
    clusterOffsets.append( 11445840 )
    clusterOffsets.append( 11693839 )
    clusterOffsets.append( 11982826 )
    clusterOffsets.append( 12452157 )
    clusterOffsets.append( 12945523 )
    clusterOffsets.append( 13279196 )
    clusterOffsets.append( 13443927 )
    clusterOffsets.append( 13613260 )
    clusterOffsets.append( 13750660 )
    clusterOffsets.append( 13932179 )
    clusterOffsets.append( 14037691 )
    clusterOffsets.append( 14239807 )
    clusterOffsets.append( 14403181 )
    clusterOffsets.append( 14633738 )
    clusterOffsets.append( 14883763 )
    clusterOffsets.append( 15256035 )
    clusterOffsets.append( 15510606 )
    clusterOffsets.append( 15908582 )
    clusterOffsets.append( 16134486 )
    clusterOffsets.append( 16531441 )
    clusterOffsets.append( 16736449 )
    clusterOffsets.append( 16940383 )
    clusterOffsets.append( 17224079 )
    clusterOffsets.append( 17444973 )
    clusterOffsets.append( 17671738 )
    clusterOffsets.append( 17822663 )
    clusterOffsets.append( 17938615 )
    clusterOffsets.append( 18110353 )
    clusterOffsets.append( 18331532 )
    clusterOffsets.append( 18600780 )
    clusterOffsets.append( 18852128 )
    clusterOffsets.append( 19095006 )
    clusterOffsets.append( 19514294 )
    clusterOffsets.append( 19991898 )
    clusterOffsets.append( 20547093 )
    clusterOffsets.append( 20925730 )
    clusterOffsets.append( 21158257 )
    clusterOffsets.append( 21530543 )
    clusterOffsets.append( 22027354 )
    clusterOffsets.append( 22543693 )
    clusterOffsets.append( 22760869 )
    clusterOffsets.append( 22830753 )
    clusterOffsets.append( 22959322 )
    return clusterOffsets


iDataOffset = 1389
iCuesOffset = 23101218
iCuesSize   = 1889
iCuesTolerance = 2048

iSeekHeadOffset = 49
iOriginalHeaderSize = 1389
iOutputSize = 4000000000
#iCuesOffset = iOutputSize - iCuesSize + iSeekHeadOffset
#print "cuesOffset: ", iCuesOffset

mkvCues   = mkvgenerator.getMKVCues()
mkvHeader = mkvgenerator.getMKVHeader(  len(mkvCues.getvalue()) )#1889)


iCuesSize = len(mkvCues.getvalue())
iHeaderSize = len(mkvHeader.getvalue())
iCuesOffset = iOutputSize - iCuesSize + iSeekHeadOffset

iSegmentHeadSize = iHeaderSize - 49
iOriginalSegmentHeadSize = iDataOffset - 59


iSeekShift =  (iHeaderSize - 49) - (iOriginalHeaderSize - 59);
iSeekShift = -2
print "Shift: ",iHeaderSize, iOriginalHeaderSize,iSeekShift

def isHeaderRequest(start):
    return int(start) is 0
def isDataRequest(start):
    return (not isHeaderRequest(start)) and (not isCuesRequest(start) and (start < iCuesOffset)  )
def isCuesRequest(start):
    return (int(start) is iCuesOffset)\
    or\
           ( (int(start) < iCuesOffset) and ( (int(start) + iCuesTolerance ) > iCuesOffset)   )


class VideoHeader_file():
    bEOF    = False
    sFilename = sHeaderPath
    filFile = None  #this is temporary
    def __init__(self, request):
        self.request = request

    def isEOF(self):
        return self.bEOF

    def cleanup(self):
        if self.filFile:
            self.filFile.close()
            self.filFile = None

    def getData(self):
        if (not self.filFile):
            #init
            self.filFile = open(self.sFilename, 'rb')

        data = self.filFile.read(abstract.FileDescriptor.bufferSize)
        if (data):
            return data

        self.bEOF = True
        return None

class VideoHeader_bytesio():
    bEOF    = False

    def __init__(self, request):
        self.request = request

    def isEOF(self):
        return self.bEOF

    def cleanup(self):
        pass

    def getData(self):
        if not self.bEOF:
            self.bEOF = True
            return mkvHeader.getvalue()

        return None

VideoHeader = VideoHeader_bytesio
#VideoHeader = VideoHeader_file
iSeekShift = 0

class VideoData():
    bEOF    = False
    sFilename = sDataPath
    filFile = None  #this is temporary
    def __init__(self, request):
        self.request = request

    def cleanup(self):
        if self.filFile:
            self.filFile.close()
            self.filFile = None

    def isEOF(self):
        return self.bEOF

    def seek(self, offset):
        if (not self.filFile):
            #init
            self.filFile = open(self.sFilename, 'rb')
        self.filFile.seek(offset)

    def getData(self):
        if (not self.filFile):
            #init
            self.filFile = open(self.sFilename, 'rb')

        data = self.filFile.read(abstract.FileDescriptor.bufferSize)
        dataSz = len(data)
        if (data):
            return data

        bEOF = True
        return None

class VideoCues_file():
    bEOF    = False
    sFilename = sCuesPath
    filFile = None  #this is temporary
    def __init__(self, request):
        self.request = request

    def isEOF(self):
        return self.bEOF

    def cleanup(self):
        if self.filFile:
            self.filFile.close()
            self.filFile = None


    def getData(self):
        if (not self.filFile):
            #init
            self.filFile = open(self.sFilename, 'rb')

        data = self.filFile.read(abstract.FileDescriptor.bufferSize)
        if (data):
            return data

        bEOF = True
        return None

class VideoCues_bytesio():
    bEOF    = False

    def __init__(self, request):
        self.request = request

    def isEOF(self):
        return self.bEOF

    def cleanup(self):
        pass

    def getData(self):
        if not self.bEOF:
            self.bEOF = True
            return mkvCues.getvalue()

        return None

VideoCues = VideoCues_bytesio
#VideoCues = VideoCues_file

class MyStreamingProducer(object):
    """
    Superclass for classes that implement the business of producing.

    @ivar request: The L{IRequest} to write the contents of the file to.
    @ivar fileObject: The file the contents of which to write to the request.
    """

    implements(interfaces.IPullProducer)

    bufferSize = abstract.FileDescriptor.bufferSize


    def __init__(self, request): #, fileObject):
        """
        Initialize the instance.
        """
        self.request = request
        #self.fileObject = fileObject


    def start(self):
        raise NotImplementedError(self.start)


    def resumeProducing(self):
        raise NotImplementedError(self.resumeProducing)


    def stopProducing(self):
        """
        Stop producing data.

        L{IPullProducer.stopProducing} is called when our consumer has died,
        and subclasses also call this method when they are done producing
        data.
        """
        #self.fileObject.close()
        self.request = None

class MyNoRangeStreamingProducer(MyStreamingProducer):
    """
    A L{StaticProducer} that writes the entire file to the request.
    """

    videoheader = None
    videodata   = None
    videocues   = None
    videoseekhead = None

    def start(self):
        self.request.registerProducer(self, False)


    def resumeProducing(self):
        if not self.request:
            return

        if (not self.videoheader):
            #create videoheader
            self.videoheader = VideoHeader(self.request)

        #use videoheader

        if (not self.videoheader.isEOF()):
            data = self.videoheader.getData()
            if data:
                # this .write will spin the reactor, calling .doWrite and then
                # .resumeProducing again, so be prepared for a re-entrant call
                self.request.write(data)
                return


        if (not self.videodata):
            self.videodata = VideoData(self.request)

        #use videodata

        if (not self.videodata.isEOF()):
            data = self.videodata.getData()
            if data:
                # this .write will spin the reactor, calling .doWrite and then
                # .resumeProducing again, so be prepared for a re-entrant call
                self.request.write(data)
                return

        if (not self.videocues):
            self.videocues = VideoCues(self.request)

        #use videocues
        if (not self.videocues.isEOF()):
            data = self.videocues.getData()
            if data:
                # this .write will spin the reactor, calling .doWrite and then
                # .resumeProducing again, so be prepared for a re-entrant call
                self.request.write(data)
                return


        self.request.unregisterProducer()
        self.request.finish()
        self.stopProducing()



    def stopProducing(self):
        if (self.videoheader):
            #stop it
            self.videoheader.cleanup()
            self.videoheader = None


        if (self.videodata):
            #stop it
            self.videodata.cleanup()
            self.videodata = None


        if (self.videocues):
            #stop it
            self.videocues.cleanup()
            self.videocues = None

        super(MyNoRangeStreamingProducer, self).stopProducing()

class MySingleRangeStreamingProducer(MyStreamingProducer):
    """
    A L{StaticProducer} that writes a single chunk of a file to the request.
    """

    def __init__(self, request, offset, size):
        """
        Initialize the instance.

        @param request: See L{StaticProducer}.
        @param fileObject: See L{StaticProducer}.
        @param offset: The offset into the file of the chunk to be written.
        @param size: The size of the chunk to write.
        """
        #MyStreamingProducer.__init__(self, request)
        super(MySingleRangeStreamingProducer, self).__init__(request)
        self.offset = offset
        self.size = size
        self.dataProvider = None

    def start(self):
        if (isCuesRequest(self.offset)):
            self.dataProvider = VideoCues(self.request)
        elif (isDataRequest(self.offset)):
            self.dataProvider = VideoData(self.request)
            iOffset = self.offset - iDataOffset + iSeekShift
            print "Ranged request actual offset:",iOffset
            if (iOffset):
                self.dataProvider.seek(iOffset)
        else:
            self.dataProvider = None
            #self.dataProvider = VideoCues(self.request)

        self.bytesWritten = 0
        self.request.registerProducer(self, 0)


    def resumeProducing(self):
        if not self.request:
            return
        if self.dataProvider and not self.dataProvider.isEOF():
            data = self.dataProvider.getData()
            if data:
                self.request.write(data)
                return

        self.request.unregisterProducer()
        self.request.finish()
        self.stopProducing()

    def stopProducing(self):
        if (self.dataProvider):
            #stop it
            self.dataProvider.cleanup()
            self.dataProvider = None
        super(MySingleRangeStreamingProducer, self).stopProducing()

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

    def getFileSize(self):
        """Return file size."""
        return iOutputSize # self.getsize()

    def _contentRange(self, offset, size):
        """
        Return a string suitable for the value of a Content-Range header for a
        range with the given offset and size.

        The offset and size are not sanity checked in any way.

        @param offset: How far into this resource the range begins.
        @param size: How long the range is.
        @return: The value as appropriate for the value of a Content-Range
            header.
        """
        return 'bytes %d-%d/%d' % (
            offset, offset + size - 1, self.getFileSize())

    def _rangeToOffsetAndSize(self, start, end):
        """
            Convert a start and end from a Range header to an offset and size.

            This method checks that the resulting range overlaps with the resource
            being served (and so has the value of C{getFileSize()} as an indirect
            input).

            Either but not both of start or end can be C{None}:

             - Omitted start means that the end value is actually a start value
               relative to the end of the resource.

             - Omitted end means the end of the resource should be the end of
               the range.

            End is interpreted as inclusive, as per RFC 2616.

            If this range doesn't overlap with any of this resource, C{(0, 0)} is
            returned, which is not otherwise a value return value.

            @param start: The start value from the header, or C{None} if one was
                not present.
            @param end: The end value from the header, or C{None} if one was not
                present.
            @return: C{(offset, size)} where offset is how far into this resource
                this resource the range begins and size is how long the range is,
                or C{(0, 0)} if the range does not overlap this resource.
            """
        size = self.getFileSize()
        if start is None:
            start = size - end
            end = size
        elif end is None:
            end = size
        elif end < size:
            end += 1
        elif end > size:
            end = size
        if start >= size:
            start = end = 0
        return start, (end - start)

    def _doSingleRangeRequest(self, request, (start, end)):
        """
        Set up the response for Range headers that specify a single range.

        This method checks if the request is satisfiable and sets the response
        code and Content-Range header appropriately.  The return value
        indicates which part of the resource to return.

        @param request: The Request object.
        @param start: The start of the byte range as specified by the header.
        @param end: The end of the byte range as specified by the header.  At
            most one of C{start} and C{end} may be C{None}.
        @return: A 2-tuple of the offset and size of the range to return.
            offset == size == 0 indicates that the request is not satisfiable.
        """




        print "_doSingleRangeRequest",start,end

        # Cases

        # 1) range request to the cues ( - up to 2048 bytes) : we return the proper offset, and the cues size
        if (isCuesRequest(start)):
            offset, size  = self._rangeToOffsetAndSize(start, end)
            offset = iCuesOffset
            size = iCuesSize
            print "\t received a Cues Request,",offset
            request.setResponseCode(tw.http.PARTIAL_CONTENT)
            request.setHeader(
                'content-range', self._contentRange(offset, size))
        # 2) range request to a cluster: we care about the offset, we don't care about the size. we can set something big on the size, it will probably work.
        elif (isDataRequest(start)):

            offset, size  = self._rangeToOffsetAndSize(start, end)
            print "\t received a Data Request,",start, end, offset,size
            request.setResponseCode(tw.http.PARTIAL_CONTENT)
            request.setHeader(
                'content-range', self._contentRange(offset, size))
        # 3 range request past the cues: request not satisfiable.
        else: #must be past cues
            if (True):
                offset = iCuesOffset
                size = iCuesSize
                print "\t received a Cues Request,",offset
                request.setResponseCode(tw.http.PARTIAL_CONTENT)
                request.setHeader(
                    'content-range', self._contentRange(offset, size))
            else:
                # This range doesn't overlap with any of this resource, so the
                # request is unsatisfiable.
                offset=size=0
                print "\t received an Unsatisfiable Request,",offset
                request.setResponseCode(tw.http.REQUESTED_RANGE_NOT_SATISFIABLE)
                request.setHeader(
                    'content-range', 'bytes */%d' % (self.getFileSize(),))
                offset, size  = self._rangeToOffsetAndSize(start, end)




        return offset, size

    def _setContentHeaders(self, request, size=None):
        """
        Set the Content-length and Content-type headers for this request.

        This method is not appropriate for requests for multiple byte ranges;
        L{_doMultipleRangeRequest} will set these headers in that case.

        @param request: The L{Request} object.
        @param size: The size of the response.  If not specified, default to
            C{self.getFileSize()}.
        """
        if size is None:
            size = iOutputSize  #23103107 #363664837  # 4000000000 #self.getFileSize()
        request.setHeader('content-length', str(size))
        if self.type:
            request.setHeader('content-type', self.type)
        if self.encoding:
            request.setHeader('content-encoding', self.encoding)

    def makeProducer_custom(self, request):
        """
        Make a L{StaticProducer} that will produce the body of this response.

        This method will also set the response code and Content-* headers.

        @param request: The L{Request} object.
        @param fileForReading: The file object containing the resource.
        @return: A L{StaticProducer}.  Calling C{.start()} on this will begin
            producing the response.
        """
        byteRange = request.getHeader('range')
        if byteRange is None:
            self._setContentHeaders(request)
            request.setResponseCode(tw.http.OK)
            return MyNoRangeStreamingProducer(request)


        print "MakeProducer: byterange: ",byteRange
        parsedRanges = self._parseRangeHeader(byteRange)


        if len(parsedRanges) == 1:
            if int(parsedRanges[0][0]) is 0:
                self._setContentHeaders(request)
#                request.setResponseCode(tw.http.PARTIAL_CONTENT)
#                request.setHeader(
#                    'content-range', self._contentRange(0, iOutputSize))
                request.setResponseCode(tw.http.OK)
                return MyNoRangeStreamingProducer(request)
            else:
                offset, size = self._doSingleRangeRequest(
                    request, parsedRanges[0])
                self._setContentHeaders(request, size)
                return MySingleRangeStreamingProducer(
                    request, offset, size)
        else:
            raise

    def makeProducer(self, request, fileForReading):
        """
        Make a L{StaticProducer} that will produce the body of this response.

        This method will also set the response code and Content-* headers.

        @param request: The L{Request} object.
        @param fileForReading: The file object containing the resource.
        @return: A L{StaticProducer}.  Calling C{.start()} on this will begin
            producing the response.
        """
        byteRange = request.getHeader('range')
        if byteRange is None:
            self._setContentHeaders(request)
            request.setResponseCode(tw.http.OK)
            return tw.static.NoRangeStaticProducer(request, fileForReading)
        try:
            parsedRanges = self._parseRangeHeader(byteRange)
        except ValueError:
            twisted.python.log.msg("Ignoring malformed Range header %r" % (byteRange,))
            self._setContentHeaders(request)
            request.setResponseCode(tw.http.OK)
            return tw.static.NoRangeStaticProducer(request, fileForReading)

        if len(parsedRanges) == 1:
            offset, size = self._doSingleRangeRequest(
                request, parsedRanges[0])
            print "Building SingleRangeStaticProducer. Offset ",offset, "Size", size
            self._setContentHeaders(request, size)
            return tw.static.SingleRangeStaticProducer(
                request, fileForReading, offset, size)
        else:
            rangeInfo = self._doMultipleRangeRequest(request, parsedRanges)
            return tw.static.MultipleRangeStaticProducer(
                request, fileForReading, rangeInfo)

    def render_GET_orig(self, request):
        """
        Begin sending the contents of this L{File} (or a subset of the
        contents, based on the 'range' header) to the given request.
        """
        self.restat(False)

        if self.type is None:
            self.type, self.encoding = tw.static.getTypeAndEncoding(self.basename(),
                                                          self.contentTypes,
                                                          self.contentEncodings,
                                                          self.defaultType)

        print "render_GET_orig: type",self.type,"encoding",self.encoding

        if not self.exists():
            return self.childNotFound.render(request)

        if self.isdir():
            return self.redirect(request)

        request.setHeader('accept-ranges', 'bytes')

        try:
            fileForReading = self.openForReading()
        except IOError, e:
            import errno
            if e[0] == errno.EACCES:
                return resource.ForbiddenResource().render(request)
            else:
                raise

        if request.setLastModified(self.getmtime()) is tw.http.CACHED:
            print "tw.http.CACHED"
            return ''


        producer = self.makeProducer(request, fileForReading)

        if request.method == 'HEAD':
            return ''

        producer.start()
        # and make sure the connection doesn't get closed
        return tw.server.NOT_DONE_YET


    def render_GET_new(self, request):
        """
        Begin sending the contents of this L{File} (or a subset of the
        contents, based on the 'range' header) to the given request.
        """

        self.path = "myH264testMovie.mkv"
        self.type = 'video/octet-stream'
        self.encoding = None

        # self.restat(False)
        #
        # if self.type is None:
        #     self.type, self.encoding = tw.static.getTypeAndEncoding(self.basename(),
        #                                                   self.contentTypes,
        #                                                   self.contentEncodings,
        #                                                   self.defaultType)
        #
        # if not self.exists():
        #     return self.childNotFound.render(request)
        #
        # if self.isdir():
        #     return self.redirect(request)

        request.setHeader('accept-ranges', 'bytes')

        # try:
        #     fileForReading = self.openForReading()
        # except IOError, e:
        #     import errno
        #     if e[0] == errno.EACCES:
        #         return resource.ForbiddenResource().render(request)
        #     else:
        #         raise

        # if request.setLastModified(self.getmtime()) is tw.http.CACHED:
        #     return ''


        producer = self.makeProducer_custom(request) #, self.path)

        if request.method == 'HEAD':
            return ''

        producer.start()
        # and make sure the connection doesn't get closed
        return tw.server.NOT_DONE_YET



    def render_GET_real(self, request):
        #return self.render_GET_orig(request)
        return self.render_GET_new(request)

    def render_GET(self, request):
        # set up the transcoding to a named pipe
        # store the pid of the transcoding process in a map
        print "render_GET: channel is ", request.channel
        # create a producer, and pass the name of the pipe

        #return File.render_GET(self, request)
        return self.render_GET_real(request)
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




print "cueOffset:",iCuesOffset
#resource = MyFile('D:/temp/streaming', defaultType='video/octet-stream')
resource = MyFile('BBBEXAMPLE', defaultType='video/octet-stream')
factory = MySite(resource)
reactor.listenTCP(8000, factory)
reactor.run()