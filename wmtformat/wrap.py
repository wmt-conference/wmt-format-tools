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

def wrap(source_xml_file, hypo_txt_file, language, name="MT"):
  """
    Wraps a hypothesis file in xml, using WMT format
    
    :param source_xml_file: An XML file containing the source documents
    :param hypo_txt_file: A text file containing the translations
    :param name: (optional) system name

    :returns: The xml, as a string.
  """
  parser = ET.XMLParser(remove_blank_text=True)
  tree = ET.parse(source_xml_file, parser)
  hypo_count = 0
  with open(hypo_txt_file) as hfh:
    for doc in tree.getroot().findall(".//doc"):
      source_segs = doc.findall(".//src//seg")
      hypo_segs = []

      for seg in source_segs:
        line = hfh.readline()
        if line == "":
          raise RuntimeError("Hypothesis file contains too few lines")
        hypo_segs.append(line.strip())
        hypo_count += 1

      # insert hyp element into doc
      hyp = ET.SubElement(doc, "hyp")
      para = ET.SubElement(hyp, "p")
      hyp.attrib["system"] = name
      hyp.attrib["lang"] = language
      for i,hypo_seg in enumerate(hypo_segs):
        seg = ET.SubElement(para, "seg")
        seg.attrib["id"] = str(i+1)
        seg.text = hypo_seg
    line = hfh.readline()
    if line != "":
      raise RuntimeError("Hypothesis file contains too many lines")

  LOG.info(f"Wrapped {hypo_count} lines of system {name}")
  return ET.tostring(tree, pretty_print=True, xml_declaration=True, encoding='utf-8').decode()

def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s:  %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--source-xml-file", help="XML source file", required=True)
  parser.add_argument("-t", "--hypo-txt-file", help="Text file containing translations, ordered as in source-file", required=True)
  parser.add_argument("-l", "--language", help="Translation language", required=True)
  parser.add_argument("-n", "--name", help="Name of MT system", default="MT")
  args = parser.parse_args()

  xmlstring = wrap(args.source_xml_file, args.hypo_txt_file, args.language, args.name)
  print(xmlstring, end="")

if __name__ == "__main__":
  main()

  
