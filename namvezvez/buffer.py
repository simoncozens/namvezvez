class BufferInfo(object):
  def __init__(self, d):
      self.__dict__ = d

class Buffer():
  def __init__(self, characters):
    self.characters = characters

  def normalize_to_glyphs(self, font):
    cmap = font.mapping
    self.info = [
      BufferInfo({
        "position": i,
        "original": x,
        "codepoint": ord(x),
        "glyph": cmap[ord(x)],
        "isMark": False,
        "mask": 0
      })

      for i,x in enumerate(self.characters)
    ]

  def set_unicode_props(self):
    pass
    # XXX

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