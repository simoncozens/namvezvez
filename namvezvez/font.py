from fontTools.misc.py23 import *
from fontTools.ttLib import TTFont
from collections import OrderedDict
from namvezvez.lookup import wrapFonttoolsLU
class GTable:
  def __init__(self, table):
    self.table = table
    self.scripts = {scriptRecord.ScriptTag: scriptRecord for scriptRecord in self.table.ScriptList.ScriptRecord}

  def getLookup(self,ix):
    fontToolsLookup = self.table.LookupList.Lookup[ix]
    return wrapFonttoolsLU(fontToolsLookup, self.table)

  def getLookups(self,feature,script,lang):
    script = self.scripts.get(script, self.scripts["DFLT"])
    langs = {l.LangSysTag: l.LangSys for l in script.Script.LangSysRecord}
    selected = langs.get(lang, script.Script.DefaultLangSys)
    features = [self.table.FeatureList.FeatureRecord[ix] for ix in selected.FeatureIndex]
    features = { f.FeatureTag:f for f in features }
    if not(feature in features): return []
    return [ self.getLookup(ix) for ix in features[feature].Feature.LookupListIndex ]

class Font:
  def __init__(self, fileOrFont):
    if isinstance(fileOrFont, TTFont):
      self.font = fileOrFont
    else:
      self.file = fileOrFont
      self.font = TTFont(fileOrFont)
    self.mapping = self.font["cmap"].getBestCmap()
    gsub_gpos = [self.font[tableTag] for tableTag in ('GSUB', 'GPOS') if tableTag in self.font]

    if "GSUB" in self.font:
      self.gsub = GTable(self.font["GSUB"].table)
    else:
      self.gsub = None
    if "GPOS" in self.font:
      self.gpos = GTable(self.font["GPOS"].table)
    else:
      self.gpos = None
