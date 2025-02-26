#!/usr/bin/env python

#
# Convert the xml format to json
#

import argparse
import json
import sys

import lxml.etree as ET

def doc2json(doc):
  """Parse a document (source,target or hypothesis)"""
  jsondoc = {}
  translator = doc.get("translator")
  if translator != None:
    jsondoc["translator"] = translator
  jsondoc["lang"] = doc.get("lang")
  paras = []
  for para in doc.findall("p"):
    jsonpara = []
    for segment in para.findall("seg"):
      jsonpara.append(segment.text)
    paras.append(jsonpara)
  jsondoc['paragraphs'] = paras
  return jsondoc

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--input', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
  parser.add_argument('-o', '--output', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
   
  args = parser.parse_args()
  tree = ET.parse(args.input).getroot()
  jsontree = {}
  jsontree['id'] = tree.get("id")
  jsontree['docs'] = []
  for doc in tree.findall("doc"):
    jsondoc = {}
    jsondoc["id"] = doc.get("id")
    jsondoc["origlang"] = doc.get("origlang")
    src = doc.find("src")
    jsonsrc = doc2json(src)
    jsondoc['src'] = jsonsrc
    refs = doc.findall("ref")
    if len(refs):
      jsondoc['ref'] = []
      for ref in refs:
        jsonref = doc2json(ref)
        jsondoc['ref'].append(jsonref)
        
      
    
    
    jsontree['docs'].append(jsondoc)

  print(json.dumps(jsontree, indent=2), file=args.output)

if __name__ == "__main__":
  main()