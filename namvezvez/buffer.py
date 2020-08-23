import youseedee
from enum import IntFlag
import namvezvez


class UnicodeProperties(IntFlag):
    GEN_CAT = 0x001F
    IGNORABLE = 0x0020
    HIDDEN = 0x0040
    CONTINUATION = 0x0080
    Cf_ZWJ = 0x0100
    Cf_ZWNJ = 0x0200


class BufferFlag(IntFlag):
    DEFAULT = 0x00000000
    HAS_NON_ASCII = 0x00000001
    HAS_DEFAULT_IGNORABLES = 0x00000002
    HAS_SPACE_FALLBACK = 0x00000004
    HAS_GPOS_ATTACHMENT = 0x00000008
    HAS_UNSAFE_TO_BREAK = 0x00000010
    HAS_CGJ = 0x00000020
    COMPLEX0 = 0x01000000
    COMPLEX1 = 0x02000000
    COMPLEX2 = 0x04000000
    COMPLEX3 = 0x08000000


class BufferInfo(object):
    def __init__(self, d):
        self.__dict__ = d


class Buffer:
    def __init__(self, characters):
        self.characters = characters
        self.scratch_flags = 0

    def normalize_to_glyphs(self, font):
        cmap = font.mapping
        self.info = [
            BufferInfo(
                {
                    "position": i,
                    "original": x,
                    "unicode_props": 0,
                    "ucd_data": youseedee.ucd_data(ord(x)),
                    "codepoint": ord(x),
                    "glyph": cmap[ord(x)],
                    "isMark": False,
                    "mask": 0,
                }
            )
            for i, x in enumerate(self.characters)
        ]

    def set_unicode_props(self):
        for i in range(0, len(self.info)):
            info = self.info[i]
            self.set_glyph_unicode_props(info)
            if (
                info.ucd_data["General_Category"] == "Sk"
                and info.codepoint >= 0x1F3FB
                and info.codepoint <= 0x1F3FF
            ):
                info.unicode_props |= UnicodeProperties.CONTINUATION
            # Not going to do emoji sequences
            elif info.codepoint >= 0xE0020 and info.codepoint <= 0xE007F:
                info.unicode_props |= UnicodeProperties.CONTINUATION

    def set_glyph_unicode_props(self, info):
        u = info.codepoint
        if info.codepoint > 0x80:
            self.scratch_flags = self.scratch_flags | BufferFlag.HAS_NON_ASCII
        if namvezvez.unicode.is_default_ignorable(info.codepoint):
            self.scratch_flags = self.scratch_flags | BufferFlag.HAS_DEFAULT_IGNORABLE
            info.unicode_props |= UnicodeProperties.IGNORABLE
            if info.codepoint == 0x200C:
                info.unicode_props |= UnicodeProperties.Cf_ZWNJ
            elif info.codepoint == 0x200D:
                info.unicode_props |= UnicodeProperties.Cf_ZWJ
            elif u >= 0x180B and u <= 0x180D:
                info.unicode_props |= UPROPS_MASK_HIDDEN

    def insert_dotted_circle(self, font):
        pass
        # XXX

    def form_clusters(self):
        pass
        # XXX

    def propagate_flags(self):
        pass

    def ensure_native_direction(self):
        pass
        # XXX

    def as_debug_string(self):
        if hasattr(self, "info"):
            return "|".join([x.glyph for x in self.info])
        else:
            return self.characters
