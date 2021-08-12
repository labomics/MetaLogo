#!/usr/bin/env python

try: 
    from setuptools import setup
except ImportError: 
    from distutils.core import setup

exec(open('MetaLogo/version.py').read())

setup(name='MetaLogo',
      version=__version__,
      description='MetaLogo is a tool for making aligned sequence logos with multiple groups of sequences of different lengths or other characteristics',
      long_description='MetaLogo is a tool for making sequence logos. Unlike other sequence logo tools, MetaLogo allows you to input sequences with different lengths or from different groups, then it can plot multiple sequence logos in one figure and align the logos to highlight the conserved patterns among different sequence groups.\
To use MetaLogo, you could visit our public webserver http://metalogo.omicsnet.org. You could also install MetaLogo as a python package to using MetaLogo in your python scripts or in your OS terminal. If you want to provide MetaLogo to people in your local network, you could also setup a webserver by using docker.\
Please check the tutorial for detailed usage of MetaLogo package and webserver (https://github.com/labomics/MetaLogo).',
      long_description_content_type = 'text/plain',
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
