from fontTools.ttLib.tables import otTables

class BaseLookup:
  def __init__(self, fonttoolsLookup):
    self.l = fonttoolsLookup
    self.forwards = True
    self.coverage = self.get_coverage()
    self.ignoremarks = self.l.LookupFlag & 0x8

  def get_coverage(self):
    return []

  def gather_precontext(self):
    return []
  def gather_postcontext(self):
    return []

  def apply_to_buffer(self, buf):
    # XXX just applies forwards
    for ix,inf in enumerate(buf.info):
      preLU  = self.gather_precontext()
      if len(preLU) > 0:
        if not self.compare_buffer_precontext(buf,ix, preLU): continue
      postLU  = self.gather_postcontext()
      if len(postLU) > 0:
        if not self.compare_buffer_postcontext(buf, ix, postLU): continue
      if not (inf.glyph in self.coverage):
        continue
      self.apply_to_context(buf, ix)

  def compare_buffer_postcontext(self, buf, ix, postLU):
    pos = 0
    mypostLU = list(postLU)
    while len(mypostLU) > 0:
      pos = pos + 1
      if ix+pos > len(buf.info)-1: return False

      # if self.ignoremarks and mypostLU[0].isMark:
      #   mypostLU.pop(0)
      if self.ignoremarks and buf.info[ix+pos].isMark:
        continue
      if isinstance(mypostLU[0], str):
        if not (mypostLU[0] == buf.info[ix+pos].glyph):
          return False
      else: # Array?
        if not (buf.info[ix+pos].glyph in mypostLU[0]): return False
      mypostLU.pop(0)
    return True

class SingleSubst(BaseLookup):
  def get_coverage(self):
    coverage = []
    for sub in self.l.SubTable:
      coverage.extend(sub.mapping.keys())
    return coverage

  def apply_to_context(self, buf, ix):
    for sub in self.l.SubTable:
      if buf.info[ix].glyph in sub.mapping:
        buf.info[ix].glyph = sub.mapping[buf.info[ix].glyph]

class LigatureSubst(BaseLookup):
  def get_coverage(self):
    coverage = []
    for sub in self.l.SubTable:
      coverage.extend(sub.ligatures.keys())
    return coverage

  def apply_to_context(self, buf, ix):
    for sub in self.l.SubTable:
      for first, ligatures in sub.ligatures.items():
        pos = ix
        for lig in ligatures:
          postLU = lig.Component
          if not self.compare_buffer_postcontext(buf, ix, postLU):
            continue
          buf.info[ix].glyph = lig.LigGlyph
          del(buf.info[ix+1:ix+len(postLU)+1])

gsubClass = {
  1: SingleSubst,
  # 2: MultipleSubst,
  # 3: AlternateSubst,
  4: LigatureSubst,
  # 5: ContextSubst,
  # 6: ChainContextSubst,
  # 7: ExtensionSubst,
  # 8: ReverseChainSingleSubst
}
gposClass = {
  # 1: SinglePos,
  # 2: PairPos,
  # 3: CursivePos,
  # 4: MarkBasePos,
  # 5: MarkLigPos,
  # 6: MarkMarkPos,
  # 7: ContextPos,
  # 8: ChainContextPos,
  # 9: ExtensionPos
}

def classForFontToolsLookup(lu,table):
  if isinstance(table, otTables.GSUB):
    return gsubClass[lu.LookupType]
  elif isinstance(table, otTables.GPOS):
    return gposClass[lu.LookupType]
  else:
    raise ValueError

def wrapFonttoolsLU(lu, table):
  cl = classForFontToolsLookup(lu, table)
  return cl(lu)
