#!/usr/bin/env python

#
# Convert the xml format to json
#

import argparse
import json
import sys

import lxml.etree as ET


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
  parser.add_argument('-o', '--output', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
   
  args = parser.parse_args()
  tree = ET.parse(args.input).getroot()
  jsonlist = []
  setid = tree.get("id")
  for doc in tree.findall("doc"):
    src = doc.find("src")
    refs = doc.findall("ref")
    src_segments = {segment.get("id") : segment.text for segment in src.findall(".//seg")}
    all_ref_segments = [
      {segment.get("id") : segment.text for segment in ref.findall(".//seg")} for ref in refs
    ]
    for i,src_segment in src_segments.items():
      segment = {}
      segment['setid'] = setid
      segment['src'] = src_segment
      segment['docid'] = doc.get('id')
      segment['origlang'] = doc.get('origlang')
      segment['srclang'] = src.get('lang')
      if src.get('translator') != None:
        segment['srctranslator'] = src.get('translator')
      if segment.get('testsuite'):
        segment['testsuite'] = segment.get('testsuite')
      segment_refs  = []
      for ref,ref_segments in zip(refs,all_ref_segments):
        if i in ref_segments:
          segment_refs.append({"text": ref_segments[i], "lang" : ref.get('lang')})
          if ref.get('translator') != None:
            segment_refs[-1]['translator'] = ref.get('translator')
      segment['refs'] = segment_refs
      
      jsonlist.append(segment)

  print(json.dumps(jsonlist, indent=2), file=args.output)

if __name__ == "__main__":
  main()