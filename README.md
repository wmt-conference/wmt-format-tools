# WMT Format Tools

Tools for handling the xml-formatted test sets and hypothesis files used in the [WMT news task](http://www.statmt.org/wmt21/translation-task.html)

## Installation

```pip install git+https://github.com/wmt-conference/wmt-format-tools.git```

## Preparing a WMT submission
1. Download the xml file containing the source (e.g. `newsdev2021.ha-en.source.xml`)
2. Extract text from the source
  ```
    wmt-unwrap -o newsdev2021.ha-en < newsdev2021.ha-en.source.xml
  ```
3. Translate text to give (eg) `newsdev2021.ha-en.hypo.en`
4. Wrap translation in xml, including team name
  ```
    wmt-wrap -s newsdev2021.ha-en.source.xml -t newsdev2021.ha-en.hypo.en -n UEDIN > newsdev2021.ha-en.hypo.en.xml
  ```
