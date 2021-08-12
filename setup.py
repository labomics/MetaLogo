#!/usr/bin/env python

try: 
    from setuptools import setup
except ImportError: 
    from distutils.core import setup

exec(open('MetaLogo/version.py').read())

setup(name='MetaLogo',
      version=__version__,
      description='MetaLogo is a tool for making aligned sequence logos with multiple groups of sequences of different lengths or other characteristics',
      author='Yaowen Chen',
      author_email='achenge07@163.com',
      url='https://github.com/labomics/MetaLogo',
      packages=['MetaLogo'],
      entry_points={
          'console_scripts': ['metalogo=MetaLogo.entry:main']
      },
      python_requires='>=3.6',                
      install_requires=[
          'biopython>=1.77',
          'matplotlib>=3.3.0',
          'numpy>=1.19.1',
          'pandas>=1.3.0',
          'scipy>=1.5.2',
          'seaborn>=0.11.1',
      ],
      extras_require={
          'webserver': [
              'dash==1.21.0',
              'dash-bootstrap-components==0.12.2',
              'Flask==2.0.1',
              'gunicorn==20.1.0',
              'plotly==5.1.0',
              'toml==0.10.2',
          ]
      }
      )
