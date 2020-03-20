class BaseShaper():
  def __init__(self, plan, font, buf, features = []):
    self.plan = plan
    self.font = font
    self.buffer =  buf
    self.features = features

  def shape(self):
    self.buffer.set_unicode_props()
    self.buffer.insert_dotted_circle(self.font)
    self.buffer.form_clusters()
    self.buffer.ensure_native_direction()
    self.preprocess_text()
    # Substitute pre
    self.substitute_default()
    self.substitute_complex()
    self.position()
    # Substitute post
    self.hide_default_ignorables()
    self.postprocess_glyphs()
    self.buffer.propagate_flags()

  def preprocess_text(self):
    pass
  def postprocess_glyphs(self):
    pass

  def substitute_default(self):
    # Rotate chars
    self.buffer.normalize_to_glyphs(self.font)
    # Setup masks
    if self.plan.fallback_mark_positioning:
      self.fallback_mark_position_recategorize_marks()

  def collect_features(self):
    return []

  def substitute_complex(self):
    self.set_glyph_props()
    if self.plan.fallback_glyph_classes:
      self.synthesize_glyph_classes()
    self.plan.substitute(self.font, self.buffer)

  def set_glyph_props(self):
    if "GDEF" in self.font.font:
      gdef = self.font.font["GDEF"].table
      for x in self.buf.info:
        x["props"] = get_glyph_props(gdef, x) # XXX
        # clear lig props
      x["syllable"] = None

  def position(self):
    pass

  def hide_default_ignorables(self):
    pass

