from namvezvez.shapers.base import BaseShaper
import namvezvez
import re

class Plan:
  def __init__(self, font, direction, script, language, features=[]):
    assert(isinstance(font, namvezvez.font.Font))
    self.font = font
    self.direction = direction
    self.script = script
    self.language = language
    self.fallback_mark_positioning = False
    self.fallback_glyph_classes = False

    # Choose complex shaper
    self.shaper = self.categorize()
    self.stages = [[]]
    if isinstance(features, str):
      self.user_features = self.parse_user_feature_string(features)
    else:
      self.user_features = features

  def execute(self, chars, features=[]):
    buf = namvezvez.Buffer(chars)
    buf.normalize_to_glyphs(self.font)
    self.collect_features()
    shaper = self.shaper(self,self.font,buf,features)
    shaper.shape()
    return buf

  def parse_user_feature_string(self, features):
    features = features.split(",")
    outfeat = []
    for f in features:
      f = f.rstrip()
      m = re.match("^([+\-]?)(\w+)",f)
      if m:
        outfeat.append( { "tag": m[2], "value": m[1] == "+"})
        continue
      m = re.match("^(\w+)=([10])",f)
      if m:
        outfeat.append( { "tag": m[1], "value": m[2] == "1"})
      else:
        outfeat.append( { "tag": f, "value": True })
    return outfeat

  def add_pause(self):
    self.stages.append([])

  def add_features(self,*tags):
    self.stages[-1].extend(tags)

  def disable_feature(self, tag):
    for s in self.stages: s.remove(tag)

  def collect_features(self):
    self.add_features("rvrn")
    self.add_pause()
    if self.direction == "LTR":
      self.add_features("ltra", "ltrm")
    elif self.direction == "RTL":
      self.add_features("rtla", "rtlm")
    self.add_features("frac", "numr", "dnom", "rand")
    self.add_features(*self.shaper.collect_features(self))
    self.add_features("abvm", "blwm", "ccmp", "locl", "mark", "mkmk", "rlig")
    if self.direction == "LTR" or self.direction == "RTL":
      self.add_features("calt", "clig", "curs", "dist", "kern", "liga", "rclt")
    else:
      self.add_features("vert")
    for uf in self.user_features:
      if not uf["value"]: # Turn it off if it's already on
        self.disable_feature(uf["tag"])
      else:
        self.add_features(uf["tag"])
    if hasattr(self.shaper, "override_features"):
      self.shaper.override_features(self)

  def categorize(self):
    if self.script == "Arab": return ArabicShaper

    if self.script in ["Mong", "Syrc", "Nkoo", "Phag", "Mand", "Mani", "Phlp", "Adlm", "Rohg", "Sogd"]:
      if self.script == self.font.supported_script(self.script).lower(): return ArabicShaper
      else: return BaseShaper

    if self.script in ["Thai", "Laoo"]: return ThaiShaper
    if self.script == "Hang": return HangulShaper
    if self.script == "Hebr": return HebrewShaper
    if self.script in ["Beng", "Deva","Gujr","Guru","Knda","Mlym","Orya","Taml","Telu","Sinh"]:
      if self.font.supported_script(self.script).endswith("3"): return USEShaper
      else: return IndicShaper
    if self.script == "Khmr": return KhmerShaper

    if self.script == "Mymr":
      if self.font.supported_script(self.script) == "mymr": return BaseShaper
      else: return MyanmarShaper

    # if self.script = "Qaag": return MyanmarZawgyiShaper
    if self.script in ['Tibt', 'Buhd', 'Hano', 'Tglg', 'Tagb', 'Limb', 'Tale',
                       'Bugi', 'Khar', 'Sylo', 'Tfng', 'Bali', 'Cham', 'Kali',
                       'Lepc', 'Rjng', 'Saur', 'Sund', 'Egyp', 'Java', 'Kthi',
                       'Mtei', 'Lana', 'Tavt', 'Batk', 'Brah', 'Cakm', 'Shrd',
                       'Takr', 'Dupl', 'Gran', 'Khoj', 'Sind', 'Mahj', 'Modi',
                       'Hmng', 'Sidd', 'Tirh', 'Ahom', 'Bhks', 'Marc', 'Newa',
                       'Gonm', 'Soyo', 'Zanb', 'Dogr', 'Gong', 'Maka', 'Nand']:
      return USEShaper
    return BaseShaper

  def substitute(self, font, buf):
    gsub = font.gsub
    if not gsub: return
    for stage in self.stages:
      for feat in stage:
        lookups = gsub.getLookups(feat,self.script, self.language)
        if len(lookups) == 0: continue
        for l in lookups:
          l.apply_to_buffer(buf)
