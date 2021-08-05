# Tutorial

## Contents

- [Tutorial](#tutorial)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Install](#install)


## Introduction

MetaLogo is a tool for making sequence logos. A sequence logo is a graphical representation of the sequence conservation of nucleotides or amino acids ([From wikipedia](https://en.wikipedia.org/wiki/Sequence_logo)). For each site, the base (nucleotides or amino acids) frequencies or information contents ([Thomas, 1986](https://pubmed.ncbi.nlm.nih.gov/3525846/)) are calculated. The higher the base, the more conservative it is.

There are serveral popular sequence logo making tools, such as [WebLogo](https://weblogo.berkeley.edu/logo.cgi), [Seq2Logo](http://www.cbs.dtu.dk/biotools/Seq2Logo/), [LogoMaker](http://github.com/jbkinney/logomaker), [ggseqlogo](https://omarwagih.github.io/ggseqlogo/) and so on. However, most of them do not support sequecnes with varied length as input, which means users can only make sequence logo for sequences with a same length. In actual scenorial, we sometimes need to check sequence patterns with all possible lengths in a sample. For example, CDR3 of B cell receptors could target to different antigens when having different lengths. Besides, sometimes we need to check if two groups of sequences have similar patterns or motifs. Thus, we developed MetaLogo, which allows users group sequences into different groups, according to lengths or others characteristics, then draw multiple sequence logos in one figure and align sequence logos to highligth the potential conserved patterns among different groups. 

MetaLogo provides several beautiful and useful layouts for multiple sequence logos, which gives people more choices for motif and pattern visualization. By developing convinient websever, we also tried to help researchers who have no coding experiences to make satisfactory sequences logos. 

## Install

MetaLogo was written in Python in Linux. If you are using Windows, you could try MetaLogo in the Windows SubSystem for Linux to make sure no unexpected errors occured when using MetaLogo to make sequence logos. 

Before install MetaLogo, you could create a new virtual python enviroment for MetaLogo, which could make it easy for you to manage python packages by isolating them from others. However, this is a optional step.

    $conda create -n metalogo python=3.7
    $conda activate metalogo

Then please clone the MetaLogo repository to your local environment and excute following commands:

    $git clone https://github.com/labomics/MetaLogo .
    $cd MetaLogo
    $pip install .

After `pip install .`, you can import MetaLogo in your scripts like below:

