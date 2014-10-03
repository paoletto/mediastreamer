#!/snacks/bin/python
"""
Ebml.py

Use this package to decode and encode EBML data. Multimedia containers WebM and
Matroska are supported. Extend support for EBML-based formats by modifying the
Tags dictionary (see bottom of file).

All native EBML Elements are defined with their own decoder/encoder class in
this package, with the following exceptions:
 - String and UTF-8 types are both treated with Pythons encoding for str()
 - Date is a subclass of SignedInteger and isn't interpreted as datetime
 - SignedInteger doesn't have an encoder

Parts of this code (bitswap operators) favours little endian CPUs (Intel)

TODO: Opensource this package?

"""

from struct import pack, unpack
from math import ceil
import binascii

import io


class Writer:

    def __init__(self, doctype, version=2):
        self.load("ebml")
        self.dtd = self.tag("EBML",
                            # EBML headers with default values are omitted
                            self.tag("DocType", String(doctype)) +
                            self.tag("DocTypeVersion", UnsignedInteger(version)) +
                            self.tag("DocTypeReadVersion", UnsignedInteger(version)))
        self.load(doctype)

    def tag(self, tagName, value=-1):
        # Lazy shorthand
        if type(value) == str:
            value = String(value).encode()

        # Unknown size
        # Some parsers have problem reading 1 byte, "\xFF", so code it with 8.
        elif value == -1:
            return self.tags[tagName] + "\x01" + ("\xFF" * 7)

        # Empty
        elif value == None:
            value = ""

        else:
            value = value.encode()

        return self.tags[tagName] + SizeInteger(len(value)).encode() + value

    def load(self, doctype):
        if doctype not in Tags:
            raise Exception("Don't know '%s' doctype" % self.doctype)

        self.tags = {}
        self.doctype = doctype

        for id, (name, t, l) in Tags[doctype].iteritems():
            self.tags[name] = UnsignedInteger(id).encode()


class Reader:
    """Light-weight, non-strict Ebml parser capable of reading unknown size
     master elements.
     """

    def __init__(self, input):
        self.input = input
        self.doctype = None
        self.tags = Tags['ebml']

        try:
            self.input.tell()
            self.seekable = True
        except (AttributeError, IOError):
            self.seekable = False

        tagsread = 0

        for tag in self:
            if tagsread == 0 and tag.name != "EBML":
                break

            if tag.name == "EBMLReadVersion":
                if tag != 1 and ReaderIgnoreEBMLVersion == False:
                    raise Exception("EBML Reader v%d required" % tag)

            if tag.name == "DocType":
                self.doctype = str(tag)
                break

            if tagsread == 8:
                break

            tagsread += 1

        if self.doctype == None:
            raise Exception("No DocType header found")

        if self.doctype not in Tags:
            raise Exception("Unrecognized DocType '%s'" % self.doctype)

        self.tags = Tags[self.doctype]

    def __del__(self):
        self.input.close()

    def __iter__(self):
        masters = [None] * (ReaderMaxMasterLevel + 1)

        while True:
            id = self.readElement(UnsignedInteger)
            size = self.readElement(SizeInteger)

            if id == None:
                for master in masters:
                    if master:
                        master.closed = True

                raise StopIteration()

            try:
                tagName, tagType, tagLevel = self.tags[id]

                if masters[tagLevel]:
                    for level in range(tagLevel, ReaderMaxMasterLevel + 1):
                        if masters[level] != None:
                            masters[level].closed = True
                            masters[level] = None

                if tagType == Master:
                    tag = Master()
                    masters[tagLevel] = tag
                    self.master = tagName
                elif size == None:
                    raise Exception("Tag %s with unknown size is invalid" % tagName)
                else:
                    data = self.input.read(size)
                    tag = tagType(data)

                tag.level = tagLevel
                tag.name = tagName

            except KeyError: # no result in self.tags
                if size != None:
                    self.seek(size)

                if ReaderIgnoreUnknown == True:
                    continue

                tag = Unknown()

            tag.id = id
            tag.size = size
            yield tag

    def dump(self):
        for tag in self:
            if tag == None:
                break

            print repr(tag)

    def seek(self, length):
        if self.seekable == False:
            return self.input.read(length)

        return self.input.seek(length, 1)

    """Reads data coded with length, as specified for 'EBML IDs' and
     'Data size' in the Matroska specification.

     Call with class constructor, e.g. UnsignedInteger for EBML IDs."""
    def readElement(self, classConstructor):
        raw = self.input.read(1)

        if not raw:
            return None

        b1 = ord(raw)

        for bytes in range(8):
            if b1 & 1 << 7 - bytes:
                if bytes:
                    raw += self.input.read(bytes)

                return classConstructor(raw)


class Element:

    def __repr__(self):
        return "%s%s%s" % (" " * self.level, self.name, self.attr())

    def attr(self):
        return ""

    def encode(self):
        return self

    def tag(self):
        data = self.encode()
        return self.id.encode() + SizeInteger(len(data)).encode() + data


class Master(Element):

    """.closed tells if this Master element have any child nodes left"""
    def __init__(self):
        self.closed = False

    def encode(self):
        raise Exception("Master tag can't be encoded")


class String(Element, str):

    def attr(self):
        return ' "%s"' % self


class Binary(String):

    def attr(self):
        return " (%d byte)" % len(self)


class Unknown(Binary):

    def __init__(self):
        self.name = "Unknown"
        self.level = 0

    def __repr__(self):
        return "Unknown id %x (%d byte)" % (self.id, len(self))


class SimpleBlock(Binary):

    def __init__(self, raw):
        flags = ord(raw[3])
        self.track = SignedInteger(raw[0])
        self.timecode = UnsignedInteger(raw[1:3])
        self.keyframe = bool(flags & 0x80)
        self.invisible = bool(flags & 0x10)
        self.discardable = bool(flags & 0x02)

    def attr(self):
        return " track %d, keyframe %s, timecode %d, data=%d" % (
        self.track, self.keyframe, self.timecode, len(self))


class UnsignedInteger(Element, long):

    def __new__(cls, *args, **kwargs):
        raw = args[0]

        if raw.__class__ in (int, long):
            return super(UnsignedInteger, cls).__new__(cls, raw)

        size = len(raw)

        if size == 3:
            raw = raw.rjust(4, "\x00")
        elif size in (5,6,7):
            raw = raw.rjust(8, "\x00")

        try:
            number = unpack(">%s" % "xBHIIQQQQ"[size], raw)[0]
        except IndexError:
            raise IndexError("Invalid integer of length %d" % size)

        return super(UnsignedInteger, cls).__new__(cls, number)

    def attr(self):
        return " %d" % self

    def encode(self):
        binlen = len(bin(self)) - 2
        size = int(ceil(binlen / 8.0))
        data = pack(">%s" % "BBHIIQQQQ"[size], self)

        if size in (3, 5, 6, 7):
            return data.lstrip("\x00")
        else:
            return data


class SizeInteger(UnsignedInteger):

    def __new__(cls, *args, **kwargs):
        raw = args[0]

        if raw.__class__ in (int, long):
            return super(UnsignedInteger, cls).__new__(cls, raw)

        # Strip size/length bit
        raw = chr(ord(raw[0]) - (1 << 8 - len(raw))) + raw[1:]

        return super(SizeInteger, cls).__new__(cls, raw)

    def encode(self):
        binlen = len(bin(self)) - 2 # -2 from pythons 0b
        size = int(ceil((binlen+1) / 7.0)) # +1 for "1 << size"
        num = self | (1 << size*7)

        try:
            data = pack(">%s" % "BBHIIQQQQ"[size], num)
        except IndexError:
            raise Exception ("Need %d bytes to encode, limited to 8" % size)

        if size in (3, 5, 6, 7):
            return data.lstrip("\x00")
        else:
            return data


class SignedInteger(UnsignedInteger):

    def __new__(cls, *args, **kwargs):
        num = super(SignedInteger, cls).__new__(cls, args[0])
        num -= (1<<8*len(args[0]))/2
        return num

    # TODO: SignedInteger.encode()


class DateElm(SignedInteger):
    pass


class Float(Element, float):

    def __new__(cls, *args, **kwargs):
        raw = args[0]

        if raw.__class__ == float:
            return super(Float, cls).__new__(cls, raw)

        if len(raw) == 4: # float
            number = unpack('>f', raw)[0]
        elif len(raw) == 8: # double float
            number = unpack('>d', raw)[0]

        return super(Float, cls).__new__(cls, number)

    def attr(self):
        return " %lf" % self

    def encode(self):
        return pack('>d', self)


"""

Sources:
http://www.webmproject.org/code/specs/container/
http://matroska.org/technical/specs/index.html

Tags = {"doctype": {EBML ID: (Element name, Element Type (class), Level)}}

"""
Tags = {
    "ebml": {
        0x1a45dfa3: ('EBML', Master, 0),
        0x4286: ('EBMLVersion', UnsignedInteger, 1),
        0x42f7: ('EBMLReadVersion', UnsignedInteger, 1),
        0x42f2: ('EBMLMaxIDLength', UnsignedInteger, 1),
        0x42f3: ('EBMLMaxSizeLength', UnsignedInteger, 1),
        0x4282: ('DocType', String, 1),
        0x4287: ('DocTypeVersion', UnsignedInteger, 1),
        0x4285: ('DocTypeReadVersion', UnsignedInteger, 1),
        },
    "webm": {
        0xec: ('Void', Binary, 0),

        # Segment
        0x18538067: ('Segment', Master, 0),

        # Seek
        0x114d9b74: ('SeekHead', Master, 1),
        0x4dbb: ('Seek', Master, 2),
        0x53ab: ('SeekID', Binary, 3),
        0x53ac: ('SeekPosition', UnsignedInteger, 3),

        # Info
        0x1549a966: ('Info', Master, 1),
        0x2ad7B1: ('TimecodeScale', UnsignedInteger, 2),
        0x4489: ('Duration', Float, 2),
        #		0x4461: ('DateUTC', DateElm, 2),
        0x7ba9: ('Title', String, 2), # Actually not WebM, only in Matroska
        0x4d80: ('MuxingApp', String, 2),
        0x5741: ('WritingApp', String, 2),

        # Cluster
        0x1f43b675: ('Cluster', Master, 1),
        0xe7: ('Timecode', UnsignedInteger, 2),
        0xab: ('PrevSize', UnsignedInteger, 2),
        0xa3: ('SimpleBlock', SimpleBlock, 2),
        0xa0: ('BlockGroup', Master, 2),
        0xa1: ('Block', Binary, 3),
        0x9b: ('BlockDuration', UnsignedInteger, 3),
        0xfb: ('ReferenceBlock', SignedInteger, 3),
        0x8e: ('Slices', Master, 3),
        0xe8: ('TimeSlice', Master, 4),
        0xcc: ('LaceNumber', UnsignedInteger, 5),

        # Track
        0x1654ae6b: ('Tracks', Master, 1),
        0xae: ('TrackEntry', Master, 2),
        0xd7: ('TrackNumber', UnsignedInteger, 3),
        0x73c5: ('TrackUID', UnsignedInteger, 3),
        0x83: ('TrackType', UnsignedInteger, 3),
        0xb9: ('FlagEnabled', UnsignedInteger, 3),
        0x88: ('FlagDefault', UnsignedInteger, 3),
        0x55aa: ('FlagForced', UnsignedInteger, 3),
        0x9c: ('FlagLacing', UnsignedInteger, 3),
        0x23e383: ('DefaultDuration', UnsignedInteger, 3),
        0x536e: ('Name', String, 3),
        0x22b59c: ('Language', String, 3),
        0x86: ('CodecID', String, 3),
        0x63a2: ('CodecPrivate', Binary, 3),
        0x258688: ('CodecName', String, 3),

        # Video
        0xe0: ('Video', Master, 3),
        0x9a: ('FlagInterlaced', UnsignedInteger, 4),
        0x53b8: ('StereoMode', UnsignedInteger, 4),
        0xb0: ('PixelWidth', UnsignedInteger, 4),
        0xba: ('PixelHeight', UnsignedInteger, 4),
        0x54aa: ('PixelCropBottom', UnsignedInteger, 4),
        0x54bb: ('PixelCropTop', UnsignedInteger, 4),
        0x54cc: ('PixelCropLeft', UnsignedInteger, 4),
        0x54dd: ('PixelCropRight', UnsignedInteger, 4),
        0x54B0: ('DisplayWidth', UnsignedInteger, 4),
        0x54BA: ('DisplayHeight', UnsignedInteger, 4),
        0x54b2: ('DisplayUnit', UnsignedInteger, 4),
        0x54b3: ('AspectRatioType', UnsignedInteger, 4),

        # Audio
        0xe1: ('Audio', Master, 3),
        0xb5: ('SamplingFrequency', Float, 4),
        0x78b5: ('OutputSamplingFrequency', Float, 4),
        0x9F: ('Channels', UnsignedInteger, 4),
        0x6264: ('BitDepth', UnsignedInteger, 4),

        # Cues
        0x1c53bb6b: ('Cues', Master, 1),
        0xbb: ('CuePoint', Master, 2),
        0xb3: ('CueTime', UnsignedInteger, 3),
        0xb7: ('CueTrackPositions', Master, 3),
        0xf7: ('CueTrack', UnsignedInteger, 4),
        0xf1: ('CueClusterPosition', UnsignedInteger, 4),
        0x5378: ('CueBlockNumber', UnsignedInteger, 4),
        },
    }

# Matroska is partly supported
Tags["matroska"] = Tags['webm']

ReaderIgnoreUnknown = True
ReaderIgnoreEBMLVersion = False
ReaderMaxMasterLevel = 5

if __name__ == '__main__':
    from sys import argv, exit

    a = Float(11.3)
    print a
    print type(a.encode())

    print binascii.hexlify((a.encode()))


    a = io.BytesIO()

    a.write("Foo")
    a.write("Bar")

    print a.getvalue()

    print len(a.getvalue())

    f='\x1C\x53\xBB\x6B'
    print f
    print len(f)
    print type(f)
    print f[3]
    print len(bytearray(f))
    print binascii.hexlify(f)

    bufSz = 2
    foo = ""
    bar = ""
    bar = a.read(bufSz)
    print "bar: ", bar
    while bar:
        foo += bar
        bar = a.read(bufSz)
        print "bar: ", bar

    print "foo:", foo

#    if len(argv) == 1:
#        print "Syntax: %s <file.mkv|file.webm>" % argv[0]
#        exit(1)
#
#    Reader(io.open(argv[1], "rb")).dump()
