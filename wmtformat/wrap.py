#!/usr/bin/env python3

#
# Wrap hypothesis for submission to WMT
#   Usage: python3 wrap.py [-n name]  -s source.xml -t hypothesis.txt > wrapped.xml
#

import argparse
import logging
import sys

import lxml.etree as ET

LOG = logging.getLogger(__name__)

def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s:  %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--source-file", help="XML source file", required=True)
  parser.add_argument("-t", "--hypo-file", help="Text file containing translations, ordered as in source-file", required=True)
  parser.add_argument("-n", "--name", help="Name of MT system", default="MT")
  args = parser.parse_args()

  parser = ET.XMLParser(remove_blank_text=True)
  tree = ET.parse(args.source_file, parser)
  with open(args.hypo_file) as hfh:
    for doc in tree.getroot().findall(".//doc"):
      source_segs = doc.findall(".//src//seg")
      hypo_segs = []

      for seg in source_segs:
        line = hfh.readline()
        if line == "":
          raise RuntimeError("Hypothesis file contains too few lines")
        hypo_segs.append(line.strip())

      # insert hyp element into doc
      hyp = ET.SubElement(doc, "hyp")
      hyp.attrib["system"] = args.name
      for i,hypo_seg in enumerate(hypo_segs):
        seg = ET.SubElement(hyp, "seg")
        seg.attrib["id"] = str(i+1)
        seg.text = hypo_seg

  sys.stdout.write(ET.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf8').decode())


if __name__ == "__main__":
  main()

  
