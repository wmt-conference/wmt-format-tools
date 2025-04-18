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
  src_segments = {segment.get("id") : (segment.text, segment.get("type")) for segment in src.findall(".//seg")}
  refs = doc.findall("ref")
  all_ref_segments = [
    {segment.get("id") : (segment.text, segment.get("type")) for segment in ref.findall(".//seg")} for ref in refs
  ]
  hyps = doc.findall("hyp")
  all_hyp_segments = [
     {segment.get("id") : (segment.text, segment.get("type")) for segment in hyp.findall(".//seg")} for hyp in hyps
  ]
  for i,(src_segment, src_type) in src_segments.items():
    segment = {}
    segment['dataset_id'] = setid
    segment['src_text'] = src_segment
    segment['doc_id'] = doc.get('id')
    segment['orig_lang'] = doc.get('origlang')
    segment['src_lang'] = src.get('lang')
    if collectionid != None:
      segment['collection_id'] = collectionid
    if src.get('translator') != None:
      segment['translator'] = src.get('translator')
    if doc.get('testsuite') != None:
      segment['testsuite'] = doc.get('testsuite')
    if doc.get('domain') != None:
      segment['domain'] = doc.get('domain')
    if src_type != None:
      segment['type'] = src_type
    segment['segment_id'] = i
    if len(refs): segment['refs'] = []
    for ref,ref_segments in zip(refs,all_ref_segments):
      if i in ref_segments:
        if ref.get('translator') != None:
          translator = ref.get('translator')
          if translator.startswith("ref") and len(translator) > 3: translator = translator[3:]
        else:
          if len(ref) > 1:
            raise RuntimeError(f"Document {segment['doc_id']} has multiple translators, but no translator ID")
          translator = "default"
        segment['refs'].append(
          {"translator" : translator,
           "tgt_lang" : ref.get('lang'),
           "text" : ref_segments[i][0]}
        )
        if ref_segments[i][1] != None:
          segment[refs][-1]['type'] = ref_segments[i][1]
    if len(hyps): segment['hyps'] = []
    for hyp,hyp_segments in zip(hyps,all_hyp_segments):
      if i in hyp_segments:
        segment['hyps'].append(
          {"system" : hyp.get('system'),
           "tgt_lang" : hyp.get('lang'),
           "text" : hyp_segments[i][0]}
        )
        if hyp_segments[i][1] != None:
          segment[hyps][-1]['type'] = hyp_segments[i][1] 
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


  for jsonitem in jsonlist:
    args.output.write(json.dumps(jsonitem, ensure_ascii=False) + "\n")

if __name__ == "__main__":
  main()