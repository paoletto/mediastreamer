import sys
import random
import math
from struct import pack, unpack
from math import ceil
import base64
from io import BytesIO

iDataSize = 4000000000
iSeekHeadSize = 512

audioCodecPrivate = base64.b16decode('118856E500')
#videoCodecPrivate = base64.b16decode('AC0164001EFFE1001B6764001EAC56240A02FF970110000003001000000303C0F162D89801000668E88E112C8B')
videoCodecPrivate = base64.b16decode('0164001effe1001b6764001eac56240a02ff970110000003001000000303c0f162d89801000668e88e112c8b'.upper())

def fillElements(map):
    g_element_names = map
    g_element_names[0xBF]       = "EBMLCrc32";
    g_element_names[0x4282]     = "EBMLDocType";
    g_element_names[0x4285]     = "EBMLDocTypeReadVersion";
    g_element_names[0x4287]     = "EBMLDocTypeVersion";
    g_element_names[0x1A45DFA3] = "EBMLHead";
    g_element_names[0x42F2]     = "EBMLMaxIdLength";
    g_element_names[0x42F3]     = "EBMLMaxSizeLength";
    g_element_names[0x42F7]     = "EBMLReadVersion";
    g_element_names[0x4286]     = "EBMLVersion";
    g_element_names[0xEC]       = "EBMLVoid";

    g_element_names[0x61A7]     = "Attached";
    g_element_names[0x1941A469] = "Attachments";
    g_element_names[0x6264]     = "AudioBitDepth";
    g_element_names[0x9F]       = "AudioChannels";
    g_element_names[0x78B5]     = "AudioOutputSamplingFreq";
    g_element_names[0x7D7B]     = "AudioPosition";
    g_element_names[0xB5]       = "AudioSamplingFreq";
    g_element_names[0xA1]       = "Block";
    g_element_names[0xEE]       = "BlockAddID";
    g_element_names[0xA5]       = "BlockAdditional";
    g_element_names[0x75A1]     = "BlockAdditions";
    g_element_names[0x9B]       = "BlockDuration";
    g_element_names[0xA0]       = "BlockGroup";
    g_element_names[0xA6]       = "BlockMore";
    g_element_names[0xA2]       = "BlockVirtual";
    g_element_names[0xB6]       = "ChapterAtom";
    g_element_names[0x437E]     = "ChapterCountry";
    g_element_names[0x80]       = "ChapterDisplay";
    g_element_names[0x4598]     = "ChapterFlagEnabled";
    g_element_names[0x98]       = "ChapterFlagHidden";
    g_element_names[0x437C]     = "ChapterLanguage";
    g_element_names[0x63C3]     = "ChapterPhysicalEquiv";
    g_element_names[0x6944]     = "ChapterProcess";
    g_element_names[0x6955]     = "ChapterProcessCodecID";
    g_element_names[0x6911]     = "ChapterProcessCommand";
    g_element_names[0x6933]     = "ChapterProcessData";
    g_element_names[0x450D]     = "ChapterProcessPrivate";
    g_element_names[0x6922]     = "ChapterProcessTime";
    g_element_names[0x1043A770] = "Chapters";
    g_element_names[0x6EBC]     = "ChapterSegmentEditionUID";
    g_element_names[0x6E67]     = "ChapterSegmentUID";
    g_element_names[0x85]       = "ChapterString";
    g_element_names[0x92]       = "ChapterTimeEnd";
    g_element_names[0x91]       = "ChapterTimeStart";
    g_element_names[0x8F]       = "ChapterTrack";
    g_element_names[0x89]       = "ChapterTrackNumber";
    g_element_names[0x6924]     = "ChapterTranslate";
    g_element_names[0x69BF]     = "ChapterTranslateCodec";
    g_element_names[0x69FC]     = "ChapterTranslateEditionUID";
    g_element_names[0x69A5]     = "ChapterTranslateID";
    g_element_names[0x73C4]     = "ChapterUID";
    g_element_names[0x1F43B675] = "Cluster";
    g_element_names[0xA7]       = "ClusterPosition";
    g_element_names[0xAB]       = "ClusterPrevSize";
    g_element_names[0x58D7]     = "ClusterSilentTrackNumber";
    g_element_names[0x5854]     = "ClusterSilentTracks";
    g_element_names[0xE7]       = "ClusterTimecode";
    g_element_names[0xAA]       = "CodecDecodeAll";
    g_element_names[0x26B240]   = "CodecDownloadURL";
    g_element_names[0x86]       = "CodecID";
    g_element_names[0x3B4040]   = "CodecInfoURL";
    g_element_names[0x258688]   = "CodecName";
    g_element_names[0x63A2]     = "CodecPrivate";
    g_element_names[0x3A9697]   = "CodecSettings";
    g_element_names[0xA4]       = "CodecState";
    g_element_names[0x4254]     = "ContentCompAlgo";
    g_element_names[0x5034]     = "ContentCompression";
    g_element_names[0x4255]     = "ContentCompSettings";
    g_element_names[0x47e1]     = "ContentEncAlgo";
    g_element_names[0x47e2]     = "ContentEncKeyID";
    g_element_names[0x6240]     = "ContentEncoding";
    g_element_names[0x5031]     = "ContentEncodingOrder";
    g_element_names[0x6d80]     = "ContentEncodings";
    g_element_names[0x5032]     = "ContentEncodingScope";
    g_element_names[0x5033]     = "ContentEncodingType";
    g_element_names[0x5035]     = "ContentEncryption";
    g_element_names[0x47e5]     = "ContentSigAlgo";
    g_element_names[0x47e6]     = "ContentSigHashAlgo";
    g_element_names[0x47e4]     = "ContentSigKeyID";
    g_element_names[0x47e3]     = "ContentSignature";
    g_element_names[0x5378]     = "CueBlockNumber";
    g_element_names[0xF1]       = "CueClusterPosition";
    g_element_names[0xEA]       = "CueCodecState";
    g_element_names[0xBB]       = "CuePoint";
    g_element_names[0x97]       = "CueRefCluster";
    g_element_names[0xEB]       = "CueRefCodecState";
    g_element_names[0xDB]       = "CueReference";
    g_element_names[0x535F]     = "CueRefNumber";
    g_element_names[0x96]       = "CueRefTime";
    g_element_names[0x1C53BB6B] = "Cues";
    g_element_names[0xB3]       = "CueTime";
    g_element_names[0xF7]       = "CueTrack";
    g_element_names[0xB7]       = "CueTrackPositions";
    g_element_names[0x4461]     = "DateUTC";
    g_element_names[0x4489]     = "Duration";
    g_element_names[0x45B9]     = "EditionEntry";
    g_element_names[0x45DB]     = "EditionFlagDefault";
    g_element_names[0x45BD]     = "EditionFlagHidden";
    g_element_names[0x45DD]     = "EditionFlagOrdered";
    g_element_names[0x45BC]     = "EditionUID";
    g_element_names[0x465C]     = "FileData";
    g_element_names[0x467E]     = "FileDescription";
    g_element_names[0x466E]     = "FileName";
    g_element_names[0x4675]     = "FileReferral";
    g_element_names[0x46AE]     = "FileUID";
    g_element_names[0x1549A966] = "Info";
    g_element_names[0x55EE]     = "MaxBlockAdditionID";
    g_element_names[0x4660]     = "MimeType";
    g_element_names[0x4D80]     = "MuxingApp";
    g_element_names[0x3E83BB]   = "NextFilename";
    g_element_names[0x3EB923]   = "NextUID";
    g_element_names[0x3C83AB]   = "PrevFilename";
    g_element_names[0x3CB923]   = "PrevUID";
    g_element_names[0xFB]       = "ReferenceBlock";
    g_element_names[0xFA]       = "ReferencePriority";
    g_element_names[0xFD]       = "ReferenceVirtual";
    g_element_names[0x4DBB]     = "Seek";
    g_element_names[0x114D9B74] = "SeekHead";
    g_element_names[0x53AB]     = "SeekID";
    g_element_names[0x53AC]     = "SeekPosition";
    g_element_names[0x18538067] = "Segment";
    g_element_names[0x4444]     = "SegmentFamily";
    g_element_names[0x7384]     = "SegmentFilename";
    g_element_names[0x73A4]     = "SegmentUID";
    g_element_names[0xA3]       = "SimpleBlock";
    g_element_names[0xCB]       = "SliceBlockAddID";
    g_element_names[0xCE]       = "SliceDelay";
    g_element_names[0xCF]       = "SliceDuration";
    g_element_names[0xCD]       = "SliceFrameNumber";
    g_element_names[0xCC]       = "SliceLaceNumber";
    g_element_names[0x8E]       = "Slices";
    g_element_names[0x7373]     = "Tag";
    g_element_names[0x45A4]     = "TagArchivalLocation";
    g_element_names[0x4EC3]     = "TagAttachment";
    g_element_names[0x5BA0]     = "TagAttachmentID";
    g_element_names[0x63C6]     = "TagAttachmentUID";
    g_element_names[0x41B4]     = "TagAudioEncryption";
    g_element_names[0x4199]     = "TagAudioGain";
    g_element_names[0x65C2]     = "TagAudioGenre";
    g_element_names[0x4189]     = "TagAudioPeak";
    g_element_names[0x41C5]     = "TagAudioSpecific";
    g_element_names[0x4488]     = "TagBibliography";
    g_element_names[0x4485]     = "TagBinary";
    g_element_names[0x41A1]     = "TagBPM";
    g_element_names[0x49C7]     = "TagCaptureDPI";
    g_element_names[0x49E1]     = "TagCaptureLightness";
    g_element_names[0x4934]     = "TagCapturePaletteSetting";
    g_element_names[0x4922]     = "TagCaptureSharpness";
    g_element_names[0x63C4]     = "TagChapterUID";
    g_element_names[0x4EC7]     = "TagCommercial";
    g_element_names[0x4987]     = "TagCropped";
    g_element_names[0x4EC8]     = "TagDate";
    g_element_names[0x4484]     = "TagDefault";
    g_element_names[0x41B6]     = "TagDiscTrack";
    g_element_names[0x63C9]     = "TagEditionUID";
    g_element_names[0x4431]     = "TagEncoder";
    g_element_names[0x6526]     = "TagEncodeSettings";
    g_element_names[0x4EC9]     = "TagEntity";
    g_element_names[0x41B1]     = "TagEqualisation";
    g_element_names[0x454E]     = "TagFile";
    g_element_names[0x67C9]     = "TagGeneral";
    g_element_names[0x6583]     = "TagGenres";
    g_element_names[0x4EC6]     = "TagIdentifier";
    g_element_names[0x4990]     = "TagImageSpecific";
    g_element_names[0x413A]     = "TagInitialKey";
    g_element_names[0x458C]     = "TagKeywords";
    g_element_names[0x22B59F]   = "TagLanguage";
    g_element_names[0x447A]     = "TagLangue";
    g_element_names[0x4EC5]     = "TagLegal";
    g_element_names[0x5243]     = "TagLength";
    g_element_names[0x45AE]     = "TagMood";
    g_element_names[0x4DC3]     = "TagMultiAttachment";
    g_element_names[0x5B7B]     = "TagMultiComment";
    g_element_names[0x5F7C]     = "TagMultiCommentComments";
    g_element_names[0x22B59D]   = "TagMultiCommentLanguage";
    g_element_names[0x5F7D]     = "TagMultiCommentName";
    g_element_names[0x4DC7]     = "TagMultiCommercial";
    g_element_names[0x5BBB]     = "TagMultiCommercialAddress";
    g_element_names[0x5BC0]     = "TagMultiCommercialEmail";
    g_element_names[0x5BD7]     = "TagMultiCommercialType";
    g_element_names[0x5BDA]     = "TagMultiCommercialURL";
    g_element_names[0x4DC8]     = "TagMultiDate";
    g_element_names[0x4460]     = "TagMultiDateDateBegin";
    g_element_names[0x4462]     = "TagMultiDateDateEnd";
    g_element_names[0x5BD8]     = "TagMultiDateType";
    g_element_names[0x4DC9]     = "TagMultiEntity";
    g_element_names[0x5BDC]     = "TagMultiEntityAddress";
    g_element_names[0x5BC1]     = "TagMultiEntityEmail";
    g_element_names[0x5BED]     = "TagMultiEntityName";
    g_element_names[0x5BD9]     = "TagMultiEntityType";
    g_element_names[0x5BDB]     = "TagMultiEntityURL";
    g_element_names[0x4DC6]     = "TagMultiIdentifier";
    g_element_names[0x6B67]     = "TagMultiIdentifierBinary";
    g_element_names[0x6B68]     = "TagMultiIdentifierString";
    g_element_names[0x5BAD]     = "TagMultiIdentifierType";
    g_element_names[0x4DC5]     = "TagMultiLegal";
    g_element_names[0x5B9B]     = "TagMultiLegalAddress";
    g_element_names[0x5BB2]     = "TagMultiLegalContent";
    g_element_names[0x5BBD]     = "TagMultiLegalType";
    g_element_names[0x5B34]     = "TagMultiLegalURL";
    g_element_names[0x5BC3]     = "TagMultiPrice";
    g_element_names[0x5B6E]     = "TagMultiPriceAmount";
    g_element_names[0x5B6C]     = "TagMultiPriceCurrency";
    g_element_names[0x5B6F]     = "TagMultiPricePriceDate";
    g_element_names[0x4DC4]     = "TagMultiTitle";
    g_element_names[0x5B33]     = "TagMultiTitleAddress";
    g_element_names[0x5BAE]     = "TagMultiTitleEdition";
    g_element_names[0x5BC9]     = "TagMultiTitleEmail";
    g_element_names[0x22B59E]   = "TagMultiTitleLanguage";
    g_element_names[0x5BB9]     = "TagMultiTitleName";
    g_element_names[0x5B5B]     = "TagMultiTitleSubTitle";
    g_element_names[0x5B7D]     = "TagMultiTitleType";
    g_element_names[0x5BA9]     = "TagMultiTitleURL";
    g_element_names[0x45A3]     = "TagName";
    g_element_names[0x4133]     = "TagOfficialAudioFileURL";
    g_element_names[0x413E]     = "TagOfficialAudioSourceURL";
    g_element_names[0x4933]     = "TagOriginalDimensions";
    g_element_names[0x45A7]     = "TagOriginalMediaType";
    g_element_names[0x4566]     = "TagPlayCounter";
    g_element_names[0x72CC]     = "TagPlaylistDelay";
    g_element_names[0x4532]     = "TagPopularimeter";
    g_element_names[0x45E3]     = "TagProduct";
    g_element_names[0x52BC]     = "TagRating";
    g_element_names[0x457E]     = "TagRecordLocation";
    g_element_names[0x1254C367] = "Tags";
    g_element_names[0x416E]     = "TagSetPart";
    g_element_names[0x67C8]     = "TagSimple";
    g_element_names[0x458A]     = "TagSource";
    g_element_names[0x45B5]     = "TagSourceForm";
    g_element_names[0x4487]     = "TagString";
    g_element_names[0x65AC]     = "TagSubGenre";
    g_element_names[0x49C1]     = "TagSubject";
    g_element_names[0x63C0]     = "TagTargets";
    g_element_names[0x63CA]     = "TagTargetType";
    g_element_names[0x68CA]     = "TagTargetTypeValue";
    g_element_names[0x4EC4]     = "TagTitle";
    g_element_names[0x63C5]     = "TagTrackUID";
    g_element_names[0x874B]     = "TagUnsynchronisedText";
    g_element_names[0x434A]     = "TagUserDefinedURL";
    g_element_names[0x65A1]     = "TagVideoGenre";
    g_element_names[0x2AD7B1]   = "TimecodeScale";
    g_element_names[0xE8]       = "TimeSlice";
    g_element_names[0x7BA9]     = "Title";
    g_element_names[0x7446]     = "TrackAttachmentLink";
    g_element_names[0xE1]       = "TrackAudio";
    g_element_names[0x23E383]   = "TrackDefaultDuration";
    g_element_names[0xAE]       = "TrackEntry";
    g_element_names[0x88]       = "TrackFlagDefault";
    g_element_names[0xB9]       = "TrackFlagEnabled";
    g_element_names[0x55AA]     = "TrackFlagForced";
    g_element_names[0x9C]       = "TrackFlagLacing";
    g_element_names[0x22B59C]   = "TrackLanguage";
    g_element_names[0x6DF8]     = "TrackMaxCache";
    g_element_names[0x6DE7]     = "TrackMinCache";
    g_element_names[0x536E]     = "TrackName";
    g_element_names[0xD7]       = "TrackNumber";
    g_element_names[0x6FAB]     = "TrackOverlay";
    g_element_names[0x1654AE6B] = "Tracks";
    g_element_names[0x23314F]   = "TrackTimecodeScale";
    g_element_names[0x6624]     = "TrackTranslate";
    g_element_names[0x66BF]     = "TrackTranslateCodec";
    g_element_names[0x66FC]     = "TrackTranslateEditionUID";
    g_element_names[0x66A5]     = "TrackTranslateTrackID";
    g_element_names[0x83]       = "TrackType";
    g_element_names[0x73C5]     = "TrackUID";
    g_element_names[0xE0]       = "TrackVideo";
    g_element_names[0x54B3]     = "VideoAspectRatio";
    g_element_names[0x2EB524]   = "VideoColourSpace";
    g_element_names[0x54BA]     = "VideoDisplayHeight";
    g_element_names[0x54B2]     = "VideoDisplayUnit";
    g_element_names[0x54B0]     = "VideoDisplayWidth";
    g_element_names[0x9A]       = "VideoFlagInterlaced";
    g_element_names[0x2383E3]   = "VideoFrameRate";
    g_element_names[0x2FB523]   = "VideoGamma";
    g_element_names[0x54AA]     = "VideoPixelCropBottom";
    g_element_names[0x54CC]     = "VideoPixelCropLeft";
    g_element_names[0x54DD]     = "VideoPixelCropRight";
    g_element_names[0x54BB]     = "VideoPixelCropTop";
    g_element_names[0xBA]       = "VideoPixelHeight";
    g_element_names[0xB0]       = "VideoPixelWidth";
    g_element_names[0x53B8]     = "VideoStereoMode";
    g_element_names[0x5741]     = "WritingApp";


mkvHeader_EBMLHeader = BytesIO()

mkvCues               = BytesIO()



EEName = {}  # EBML Element Name
fillElements(EEName)
EEID  = {}                  # EBML Element ID
for key, value in EEName.iteritems():
    EEID[value] = key

class Element:

    def __repr__(self):
        return "%s%s%s" % (" " * self.level, self.name, self.attr())

    def attr(self):
        return ""

    def encode(self):
        return self

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


# unsigned
def big_endian_number(number):
    if(number<0x100):
        return chr(number)
    return big_endian_number(number>>8) + chr(number&0xFF)

ben=big_endian_number

def ebml_encode_number(number):
    def trailing_bits(rest_of_number, number_of_bits):
        # like big_endian_number, but can do padding zeroes
        if number_of_bits==8:
            return chr(rest_of_number&0xFF);
        else:
            return trailing_bits(rest_of_number>>8, number_of_bits-8) + chr(rest_of_number&0xFF)

    if number == -1:
        return chr(0xFF)
    if number < 2**7 - 1:
        return chr(number|0x80)
    if number < 2**14 - 1:
        return chr(0x40 | (number>>8)) + trailing_bits(number, 8)
    if number < 2**21 - 1:
        return chr(0x20 | (number>>16)) + trailing_bits(number, 16)
    if number < 2**28 - 1:
        return chr(0x10 | (number>>24)) + trailing_bits(number, 24)
    if number < 2**35 - 1:
        return chr(0x08 | (number>>32)) + trailing_bits(number, 32)
    if number < 2**42 - 1:
        return chr(0x04 | (number>>40)) + trailing_bits(number, 40)
    if number < 2**49 - 1:
        return chr(0x02 | (number>>48)) + trailing_bits(number, 48)
    if number < 2**56 - 1:
        return chr(0x01) + trailing_bits(number, 56)
    raise Exception("NUMBER TOO BIG")

def ebml_element(element_id, data, length=None):
    if length==None:
        length = len(data)
    return big_endian_number(element_id) + ebml_encode_number(length) + data

def random_uid():
    def rint():
        return int(random.random()*(0x100**4))
    return ben(rint()) + ben(rint()) + ben(rint()) + ben(rint())



def fillEBMLHeader(mkvHeader_EBMLHeader, fTotalLengthMs, fFPS, vecResolution, iCuesSize):
    mkvHeader_EBMLHead = BytesIO()
    mkvHeader_EBMLSegment = BytesIO()

    def fillEBMLHead(mkvHeader_EBMLHead):
        # Write EBML header
        mkvHeader_EBMLHead.write(
                                ebml_element(EEID["EBMLHead"], "" # EBML
                                + ebml_element(EEID["EBMLVersion"], ben(1))   # EBMLVersion
                                + ebml_element(EEID["EBMLReadVersion"], ben(1))   # EBMLReadVersion
                                + ebml_element(EEID["EBMLMaxIdLength"], ben(4))   # EBMLMaxIDLength
                                + ebml_element(EEID["EBMLMaxSizeLength"], ben(8))   # EBMLMaxSizeLength
                                + ebml_element(EEID["EBMLDocType"], "matroska") # DocType
                                + ebml_element(EEID["EBMLDocTypeVersion"], ben(4))   # DocTypeVersion
                                + ebml_element(EEID["EBMLDocTypeReadVersion"], ben(2))   # DocTypeReadVersion
        ))

    def fillEBMLSegment(mkvHeader_EBMLSegment, fTotalLengthMs, fFPS, vecResolution, iCuesSize):

        mkvHeader_SeekHead = BytesIO()

        mkvHeader_SegmentInfo = BytesIO()

        mkvHeader_SegmentTracks = BytesIO()

        def fillEBMLSeekHead(mkvHeader_SeekHead,mkvHeader_SegmentInfo, iCuesSize):
            mkvHeader_EBMLVoidPad = BytesIO()
            mkvHeader_EBMLSeekHeadContent = BytesIO()

            mkvHeader_EBMLSeekHeadContent.write(
                ebml_element(EEID["SeekHead"], "" # SegmentInfo
                    + ebml_element(EEID["Seek"], ""
                        + ebml_element(EEID["SeekID"], '\x15\x49\xA9\x66' ) #KaxInfo
                        + ebml_element(EEID["SeekPosition"], ben(iSeekHeadSize))
                    )
                    +  ebml_element(EEID["Seek"], ""
                        + ebml_element(EEID["SeekID"], '\x16\x54\xAE\x6B' ) #KaxTracks
                        + ebml_element(EEID["SeekPosition"], ben(iSeekHeadSize+len(mkvHeader_SegmentInfo.getvalue())))
                    )
                    + ebml_element(EEID["Seek"], ""
                        + ebml_element(EEID["SeekID"], '\x1C\x53\xBB\x6B' ) #KaxCues
                        + ebml_element(EEID["SeekPosition"], ben(iDataSize - iCuesSize))
                    )
                )
            )

            mkvHeader_SeekHead.write(mkvHeader_EBMLSeekHeadContent.getvalue())
            iVoidSize = iSeekHeadSize - len(mkvHeader_EBMLSeekHeadContent.getvalue())
            mkvHeader_EBMLVoidPad.write(ebml_element(EEID["EBMLVoid"], bytearray(iVoidSize)))
            mkvHeader_SeekHead.write(mkvHeader_EBMLVoidPad.getvalue())

        def fillEBMLSegmentInfo(mkvHeader_SegmentInfo, fTotalLengthMs):

            mkvHeader_SegmentInfo.write(
                ebml_element(EEID["Info"], "" # SegmentInfo
                    + ebml_element(EEID["TimecodeScale"], ben(1000000)) #milliseconds
                    + ebml_element(EEID["Title"], "MediaStreamer content")
                    + ebml_element(EEID["MuxingApp"], "MediaStreamer")
                    + ebml_element(EEID["WritingApp"], "MediaStreamer") # WritingApp
                    + ebml_element(EEID["SegmentUID"], random_uid())
                    + ebml_element(EEID["Duration"], Float(fTotalLengthMs).encode())
                )
            )

        def fillEBMLSegmentTracks(mkvHeader_SegmentTracks, fFPS, vecResolution):
            mkvHeader_SegmentTracks.write(
                ebml_element(EEID["Tracks"], "" # SegmentInfo
                    + ebml_element(EEID["TrackEntry"], ""
                        + ebml_element(EEID["TrackNumber"], ben(1))
                        + ebml_element(EEID["TrackUID"], ben(1))
                        + ebml_element(EEID["TrackFlagLacing"], ben(0))
                        + ebml_element(EEID["TrackLanguage"], "und")
                        + ebml_element(EEID["CodecID"], "V_MPEG4/ISO/AVC")
                        + ebml_element(EEID["TrackType"], ben(1)) #video
                        + ebml_element(EEID["TrackDefaultDuration"], ben(int(1.0/fFPS*1000000000.0)))
                        + ebml_element(EEID["TrackVideo"], ""
                            + ebml_element(EEID["VideoPixelWidth"], ben(vecResolution[0]))
                            + ebml_element(EEID["VideoPixelHeight"], ben(vecResolution[1]))
                            + ebml_element(EEID["VideoDisplayWidth"], ben(vecResolution[0]))
                            + ebml_element(EEID["VideoDisplayHeight"], ben(vecResolution[1]))
                        )
                        + ebml_element(EEID["CodecPrivate"], videoCodecPrivate)
                    )
                    + ebml_element(EEID["TrackEntry"], ""
                        + ebml_element(EEID["TrackNumber"], ben(2) )
                        + ebml_element(EEID["TrackUID"], ben(2))
                        + ebml_element(EEID["TrackFlagLacing"], ben(0))
                        + ebml_element(EEID["TrackLanguage"], "und")
                        + ebml_element(EEID["CodecID"], "A_AAC")
                        + ebml_element(EEID["TrackType"], ben(2)) #audio
                        + ebml_element(EEID["TrackAudio"], ""
                            + ebml_element(EEID["AudioChannels"], ben(1))
                            + ebml_element(EEID["AudioSamplingFreq"], Float(48000.0).encode() )
                            + ebml_element(EEID["AudioBitDepth"], ben(32))
                        )
                        + ebml_element(EEID["CodecPrivate"], audioCodecPrivate)
                    )
                )
            )




        fillEBMLSegmentInfo(mkvHeader_SegmentInfo, fTotalLengthMs)
        fillEBMLSegmentTracks(mkvHeader_SegmentTracks, fFPS, vecResolution)
        fillEBMLSeekHead(mkvHeader_SeekHead,mkvHeader_SegmentInfo, iCuesSize)

        mkvHeader_EBMLSegment.write(ebml_element(EEID["Segment"], "", iDataSize))
        mkvHeader_EBMLSegment.write(mkvHeader_SeekHead.getvalue())
        mkvHeader_EBMLSegment.write(mkvHeader_SegmentInfo.getvalue())
        mkvHeader_EBMLSegment.write(mkvHeader_SegmentTracks.getvalue())

    fillEBMLHead(mkvHeader_EBMLHead)
    fillEBMLSegment(mkvHeader_EBMLSegment,fTotalLengthMs, fFPS, vecResolution, iCuesSize)

    mkvHeader_EBMLHeader.write(mkvHeader_EBMLHead.getvalue())
    mkvHeader_EBMLHeader.write(mkvHeader_EBMLSegment.getvalue())

def fillEBMLCues(mkvCues):
    pass



if __name__ == '__main__':
    fillEBMLHeader(mkvHeader_EBMLHeader,634621.0,30.0,(640,360),1889)

    fileOut = open("/tmp/testHeader.mkv",'wb')
    fileOut.write(mkvHeader_EBMLHeader.getvalue())
    fileOut.close()







def foo():
    mp3file = open("q.mp3", "rb")
    mp3file.read(500000);

    def mp3framesgenerator(f):
        debt=""
        while True:
            for i in xrange(0,len(debt)+1):
                if i >= len(debt)-1:
                    debt = debt + f.read(8192)
                    break
                    #sys.stderr.write("i="+str(i)+" len="+str(len(debt))+"\n")
                if ord(debt[i])==0xFF and (ord(debt[i+1]) & 0xF0)==0XF0 and i>700:
                    if i>0:
                        yield debt[0:i]
                        #   sys.stderr.write("len="+str(i)+"\n")
                        debt = debt[i:]
                        break


    mp3 = mp3framesgenerator(mp3file)
    mp3.next()


    for i in xrange(0,530):
        framefile = open("img/"+str(i)+".jpg", "rb")
        framedata = framefile.read()
        framefile.close()

        # write cluster (actual video data)

        if random.random()<1:
            sys.stdout.write(ebml_element(0x1F43B675, "" # Cluster
                                                      + ebml_element(0xE7, ben(int(i*26*4))) # TimeCode, uint, milliseconds
            # + ebml_element(0xA7, ben(0)) # Position, uint
            + ebml_element(0xA3, "" # SimpleBlock
                                 + ebml_encode_number(1) # track number
                                 + chr(0x00) + chr(0x00) # timecode, relative to Cluster timecode, sint16, in milliseconds
                                 + chr(0x00) # flags
            + framedata
            )))

        for u in xrange(0,4):
            mp3f=mp3.next()
            if random.random()<1:
                sys.stdout.write(ebml_element(0x1F43B675, "" # Cluster
                                                          + ebml_element(0xE7, ben(i*26*4+u*26)) # TimeCode, uint, milliseconds
                + ebml_element(0xA3, "" # SimpleBlock
                                     + ebml_encode_number(2) # track number
                                     + chr(0x00) + chr(0x00) # timecode, relative to Cluster timecode, sint16, in milliseconds
                                     + chr(0x00) # flags
                + mp3f
                )))





