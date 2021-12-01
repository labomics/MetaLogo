#!/usr/bin/env python

try: 
    from setuptools import setup
except ImportError: 
    from distutils.core import setup

exec(open('MetaLogo/version.py').read())

setup(name='MetaLogo',
      version=__version__,
      description='MetaLogo is a heterogeneity-aware sequence logo generator and aligner',
      long_description='MetaLogo is a tool for making sequence logos. It can take multiple sequences as input, automatically identify the homogeneity and heterogeneity among sequences and cluster them into different groups given any wanted resolution, finally output multiple aligned sequence logos in one figure. Grouping can also be specified by users, such as grouping by lengths, grouping by sample Id, etc.  Compared to conventional sequence logo generator, MetaLogo can display the total sequence population in a more detailed, dynamic and informative view. homogeneity.\
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
          'toml>=0.10.2',
          'treecluster>=1.0.3',
          'dendropy>=4.5.2',
          'ete3>=3.1.1',
      ],
      extras_require={
          'webserver': [
              'dash==1.21.0',
              'dash-bio==0.8.0',
              'dash-bootstrap-components==0.12.2',
              'Flask==2.0.1',
              'gunicorn==20.1.0',
              'plotly==5.1.0',
              'supervisor==4.2.2',
              'rq==1.10.0',
              'hiredis==2.0.0',
          ]
      }
      )
