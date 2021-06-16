#!/usr/bin/env python3

#
# Extract source and reference (if it exists)
#   Usage: python3 unwrap.py -o newstest2021 [ARGS] < testset.xml
#

import argparse
import logging
import sys

import lxml.etree as ET

LOG = logging.getLogger(__name__)

DEFAULT_TRANSLATOR = "DEFAULT"

def unwrap(xml_file, missing_message="NO TRANSLATION AVAILABLE", document_boundaries=False):
  """
  Unwraps an xml file in WMT format, producing source and (if present) reference files

  :param xml_file: The xml file (or fd)
  :param missing_message: The message to insert when no reference

  :returns: A tuple src-lang, src-lines, ref-lang, {translator-A : reflines-A, ...}

  If there is no reference, ref-lang is None, and the dictionary is empty.
  """
  tree = ET.parse(xml_file) 

  # Find and check  the source langs, ref langs and translators
  src_langs, ref_langs, translators = set(), set(), set()

  for src_doc in tree.getroot().findall(".//src"):
    src_langs.add(src_doc.get("lang"))

  for ref_doc in tree.getroot().findall(".//ref"):
    ref_langs.add(ref_doc.get("lang"))
    translator = ref_doc.get("translator")
    if translator: translators.add(translator)
  
  if len(src_langs) >  1:
    raise RuntimeError("Multiple source languages found")

  if len(src_langs) == 0:
    raise RuntimeError("No source languages found")

  src_lang = src_langs.pop()
  src = []

  if len(ref_langs) > 1:
    raise RuntimeError("Multiple reference languages found -- this case is not currently handled")


  if len(ref_langs) > 0:
    if len(translators) == 0:
      LOG.info("No translator identifiers found -- reading first translation for each document")
      translators.add(DEFAULT_TRANSLATOR)
    ref_lang = ref_langs.pop()
    ref = {translator : [] for translator in translators}
  else:
    LOG.info("No references found")
    ref_lang = None
    ref = {}


  # Extract text
  src_sent_count,doc_count = 0,0
  for doc in tree.getroot().findall(".//doc"):
    if document_boundaries and doc_count:
      src.append("")
      for ref_set in ref.values():
        ref_set.append("")
    doc_count += 1
    src_sents = {int(seg.get("id")): seg.text for seg in doc.findall(".//src//seg")}
    if ref_lang:
      ref_docs = doc.findall(".//ref")
      trans_to_ref = {}

      # If no translator identifiers, we just read one reference (if any) 
      # If there are translator identifiers, we add a reference for each translator

      def get_ref_sents(ref_doc):
        return {int(seg.get("id")): seg.text for seg in ref_doc.findall(f".//seg")}

      if len(translators) == 1 and DEFAULT_TRANSLATOR in translators:
        if len(ref_docs):
          trans_to_ref[DEFAULT_TRANSLATOR] = get_ref_sents(ref_docs[0])
        else:
          trans_to_ref[DEFAULT_TRANSLATOR] = {}
      else:
        trans_to_ref  = {ref_doc.get("translator"): get_ref_sents(ref_doc) for ref_doc in ref_docs}

    for seg_id in sorted(src_sents.keys()):
      src.append(src_sents[seg_id])
      src_sent_count += 1
      if ref_lang:
        for translator in translators:
          ref[translator].append(trans_to_ref.get(translator, {translator: {}}).get(seg_id, missing_message))

  LOG.info(f"Extracted {doc_count} document(s) containing {src_sent_count} sentences in {src_lang}")


  return src_lang,src,ref_lang,ref

def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s:  %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--in-file", type=argparse.FileType('r'), default=sys.stdin)
  parser.add_argument("--translator", help="Which translator to use for the reference side")
  parser.add_argument("-o", "--out-stem", required=True)
  parser.add_argument("-m", "--missing-translation-message", default="NO TRANSLATION AVAILABLE", help="Message to insert when translations are missing")
  parser.add_argument("-d", "--document-boundaries", action="store_true", help="Mark document boundaries by an empty line")
  args = parser.parse_args()

  src_lang, src, ref_lang, ref = unwrap(args.in_file, args.missing_translation_message, args.document_boundaries)
 
  # Check translator
  if ref_lang:
    if args.translator != None:
      if  args.translator not in ref:
        raise RuntimeError(f"Translator {args.translator} was not found")
      else:
        LOG.info(f"Selecting references from translator {args.translator}")

    if args.translator == None:
      if len(ref) > 1:
        raise RuntimeError("Multiple translators -- need to specify which one to choose")
      else:
        LOG.info("Selecting the only translation")
  else:
    if args.translator != None:
      raise RuntimeError("Translator specified, but no reference found")

  # write source
  src_file = f"{args.out_stem}.{src_lang}"
  LOG.info(f"Extracting {src_lang} sentences to {src_file}")
  with open(src_file, "w") as sfh:
    for line in src:
      print(line, file=sfh)

  # optionally write refs
  if ref_lang:
    ref_file = f"{args.out_stem}.{ref_lang}"
    LOG.info(f"Extracting {ref_lang} sentences to {ref_file}")
    if args.translator:
      ref_lines = ref[args.translator]
    else:
      # Should only be one reference
      ref_lines = list(ref.values())[0]
    with open(ref_file, "w") as rfh:
      for line in ref_lines:
        print(line, file=rfh)


if __name__ == "__main__":
  main()

  
