from distutils.core import setup

setup(
  name = "wmtformat",
  version = "0.1",
  packages=['wmtformat',],
  install_requires = [
  ],
  license = 'Apache License 2.0',
  entry_points={
    'console_scripts' : [
      'wmt-wrap = wmtformat.wrap:main',
      'wmt-unwrap = wmtformat.unwrap:main',
    ],
  },
)

