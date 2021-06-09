#!/usr/bin/env python

import sys
from pathlib import Path

import wmtformat

def main():
  sampledir = Path(sys.argv[0]).parent / "sample-data"

  wrapped = wmtformat.wrap((sampledir / "sample-src.xml").as_posix(), sampledir / "sample-hyp.ha", name="test-team")
  with open("out.xml", "w") as ofh:
    print(wrapped, file=ofh, end="")



if __name__ == "__main__":
  main()
