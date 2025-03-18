#!/usr/bin/env python

#
# Convert the xml format to json
#

import argparse
import json
import sys

import lxml.etree as ET

def processDoc(doc, setid, collectionid, jsonlist):
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
    if collectionid != None:
      segment['collectionid'] = collectionid
    if src.get('translator') != None:
      segment['srctranslator'] = src.get('translator')
    if doc.get('testsuite'):
      segment['testsuite'] = doc.get('testsuite')
    if segment.get('type'):
      segment['type'] = segment.get('type')
    for ref,ref_segments in zip(refs,all_ref_segments):
      if i in ref_segments:
        if ref.get('translator') != None:
          translator = ref.get('translator')
          if translator.startswith("ref") and len(translator) > 3: translator = translator[3:]
        else:
          if len(ref) > 1:
            raise RuntimeError(f"Document {segment['docid']} has multiple translators, but no translator ID")
          translator = "0"
        segment[f"ref{translator}"] = ref_segments[i]
        segment[f"ref{translator}lang"] = ref.get('lang')
    jsonlist.append(segment)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
  parser.add_argument('-o', '--output', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
   
  args = parser.parse_args()
  tree = ET.parse(args.input).getroot()
  jsonlist = []
  setid = tree.get("id")
  for col_or_doc in tree:
    if col_or_doc.tag == "collection":
      for doc in col_or_doc:
        processDoc(doc, setid, col_or_doc.get('id'), jsonlist)
    else:
      processDoc(col_or_doc, setid, None, jsonlist)


  print(json.dumps(jsonlist, indent=2), file=args.output)

if __name__ == "__main__":
  main()