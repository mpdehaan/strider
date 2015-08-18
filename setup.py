#!/usr/bin/python


import os
import sys

from setuptools import setup, find_packages

setup(name='strider',
      version="0.0.2",
      description='Strider is a python dev/test VM workflow tool, similar to Vagrant',
      author='Michael DeHaan',
      author_email='michael.dehaan@gmail.com',
      url='http://github.com/mpdehaan/strider/',
      license='Apache2',
      install_requires=['boto'],
      package_dir={ '': 'lib' },
      packages=find_packages('lib'),
      classifiers=[
      ],
      scripts=[
      ],
      data_files=[
      ],
)
