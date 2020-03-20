from fontTools.ttLib.tables import otTables

class BaseLookup:
  def __init__(self, fonttoolsLookup):
    self.l = fonttoolsLookup
    self.forwards = True
    self.coverage = self.get_coverage()

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
        preBuf = self.gather_buffer_precontext(buf, ix)
        if not self.compare_context(preLu, preBuf): continue
      postLU  = self.gather_postcontext()
      if len(postLU) > 0:
        postBuf = self.gather_buffer_postcontext(buf, ix)
        if not self.compare_context(postLu, postBuf): continue
      if not (inf.glyph in self.coverage):
        continue
      self.apply_to_context(buf, ix)

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

gsubClass = {
  1: SingleSubst,
  # 2: MultipleSubst,
  # 3: AlternateSubst,
  # 4: LigatureSubst,
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
