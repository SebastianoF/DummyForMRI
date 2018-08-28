#!/usr/bin/env python

from DummyForMRI.__init__ import __version__
from setuptools import setup, find_packages


setup(name='DummyForMRI',
      version=__version__,
      description='Creation of a very simple neuroimage Dummy in infti format to test pipelines and basic algorithms.',
      author='sebastiano ferraris',
      author_email='sebastiano.ferraris@gmail.com',
      license='MIT',
      url='https://github.com/SebastianoF/DummyForMRI',
      packages=find_packages(),
     )

