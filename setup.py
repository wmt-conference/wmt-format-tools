from distutils.core import setup

setup(
  name = "wmtformat",
  version = "0.4",
  packages=['wmtformat',],
  license = 'Apache License 2.0',
  entry_points={
    'console_scripts' : [
      'wmt-wrap = wmtformat.wrap:main',
      'wmt-unwrap = wmtformat.unwrap:main',
    ],
  },
  install_requires=[
    'lxml',
  ]
)

