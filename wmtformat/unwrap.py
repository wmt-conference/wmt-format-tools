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


def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s:  %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--in-file", type=argparse.FileType('r'), default=sys.stdin)
  parser.add_argument("--translator", help="Which translator to use for the reference side")
  parser.add_argument("-o", "--out-stem", required=True)
  parser.add_argument("-m", "--missing-translation-message", default="NO TRANSLATION AVAILABLE", help="Message to insert when translations are missing")
  args = parser.parse_args()

  tree = ET.parse(args.in_file) 

  #TODO: Handle multiple translators

  # Find and check  the source langs, ref langs and translators
  src_langs, ref_langs, translators = set(), set(), set()
  for src_doc in tree.getroot().findall(".//src"):
    src_langs.add(src_doc.get("lang"))

  for ref_doc in tree.getroot().findall(".//ref"):
    ref_langs.add(ref_doc.get("lang"))
    #translator = ref_doc.get("translator")
    #translators.add(translator)
  
  if len(src_langs) >  1:
    raise RuntimeError("Multiple source languages found")

  if len(src_langs) == 0:
    raise RuntimeError("No source languages found")

  if len(ref_langs) > 1:
    raise RuntimeError("Multiple reference languages found -- this case is not currently handled")


  # There is exactly one of these
  src_lang = src_langs.pop()

  src_file = f"{args.out_stem}.{src_lang}"
  LOG.info(f"Extracting {src_lang} sentences to {src_file}")

  rfh = None
  if len(ref_langs) > 0:
    ref_lang = ref_langs.pop()
    ref_file = f"{args.out_stem}.{ref_lang}"
    LOG.info(f"Extracting {ref_lang} sentences to {ref_file}")
    rfh = open(ref_file, "w")
  else:
    LOG.warn("No reference languages found -- not creating reference file")

  # Extract text
  src_sent_count,ref_sent_count,doc_count = 0,0,0
  with open(f"{args.out_stem}.{src_lang}", "w") as sfh:
    for doc in tree.getroot().findall(".//doc"):
      doc_count += 1
      src_sents = {int(seg.get("id")): seg.text for seg in doc.findall(".//src//seg")}
      if rfh:
        ref_sents = {int(seg.get("id")): seg.text for seg in doc.findall(f".//ref//seg")}
        #ref_sents = {int(seg.get("id")): seg.text for seg in doc.findall(f".//ref[@translator='{args.translator}']//seg")}
      for seg_id in sorted(src_sents.keys()):
        print(src_sents[seg_id], file=sfh)
        src_sent_count += 1
        if rfh:
          ref_sent = ref_sents.get(seg_id, args.missing_translation_message)
          print(ref_sent, file=rfh)
          ref_sent_count += 1

    LOG.info(f"Extracted {doc_count} document(s) containing {src_sent_count} sentences in {src_lang}")
    if rfh:
      LOG.info(f"... and {ref_sent_count} sentences in {ref_lang}")
      rfh.close()


if __name__ == "__main__":
  main()

  
