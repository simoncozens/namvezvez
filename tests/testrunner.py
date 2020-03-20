#!/usr/bin/python
import os
mydir = os.path.dirname(os.path.abspath(__file__))
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
import namvezvez
import json, tempfile, re, glob, unittest

def read_expectations(filename):
  featurecode = ""
  tests = []
  settings = {
    "direction": "LTR",
    "script": "Latn",
    "language": 'ENG'
  }
  with open(filename) as file_in:
    for line in file_in:
      line = line.rstrip()
      if line.startswith(" ") or line.startswith("\t"):
        featurecode = featurecode + line
      elif line.startswith("#") or line == "\n":
        continue
      elif "=" in line:
        key, val = line.split("=")
        settings[key] = val
      elif ":" in line:
        test, results = line.split(":")
        features = ""
        if test.startswith("["):
          m = re.match("\[([^]]+)\](.*)", test)
          features = m[1]
          test = m[2]
        tests.append({"input": test, "expected": results, "features": features})
  return featurecode, tests, settings

def create_cached_font(featurecode):
  try:
    with open(mydir+"/fontcache.json", 'r') as f:
      cache = json.load(f)
  except (IOError, ValueError):
      cache = {}

  if featurecode not in cache:
    font = TTFont(mydir+"/FallbackPlus-Regular.otf")
    addOpenTypeFeaturesFromString(font, featurecode)
    _,tmp = tempfile.mkstemp(suffix=".otf")
    font.save(tmp)
    cache[featurecode] = tmp
    json.dump(cache, open(mydir+"/fontcache.json", 'w'))

  return namvezvez.Font(cache[featurecode])

class TestRunner(unittest.TestCase):
  def test(self):
    for testfile in glob.glob(mydir+"/*.test"):
      print("Running "+os.path.basename(testfile))
      featurecode, tests, settings = read_expectations(testfile)
      font = create_cached_font(featurecode)
      for t in tests:
        plan = namvezvez.Plan(font,
                             settings["direction"],
                             settings["script"],
                             settings["language"],
                             t["features"])
        out = plan.execute(t["input"]).as_debug_string()
        self.assertEqual(t["expected"], out)

if __name__ == '__main__':
  unittest.main()