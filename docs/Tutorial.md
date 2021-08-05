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

After install, you can import MetaLogo in your scripts or notebook like below:

![notebook](../pngs/notebook.PNG)

You can also call MetaLogo by directly type metalogo in your terminal:

![terminal](../pngs/metalogo.terminal.PNG)

If you don't want to install MetaLogo package or commands to your system, you could run the entrypoint script directly after installing all the requirements:

    $pip install -r requirements.txt
    $python -m MetaLogo.entry -h

MetaLogo also provides webserver to conviniently make sequence logos. The MetaLogo webserver was developed by using [Dash](https://dash.plotly.com/), which is a ligthweight tool for python apps development. For a temporary webserver for interactive operations, you need to install server related packages first by using following commands:

    $pip install .[webserver]

Then you could run a development Dash webserver with Debug mode on:

    $cat server.dev.sh
     python -m server.main
    $sh server.dev.sh
     Dash is running on http://127.0.0.1:8050/
     * Serving Flask app 'main' (lazy loading)
     * Environment: production
     WARNING: This is a development server. Do not use it in a production deployment.
     Use a production WSGI server instead.
     * Debug mode: on

A MetaLogo webserver will be like:
    
![Webserver](../pngs/server.PNG)

For a production server, you can build a docker container to provide the service:

    $cat server.docker.sh
     docker build -t metalogo:v1 .
     docker run -d  --expose 8050 --name metalogo -e VIRTUAL_HOST=metalogo.omicsnet.org -v "$(pwd)":/code metalogo:v1 
    $sh server.docker.sh
     ...
    $docker ps
     CONTAINER ID    IMAGE          COMMAND                  CREATED      STATUS      PORTS       NAMES
     ad598ca936df    metalogo:v1    "/bin/sh -c 'GUNICORN"   2 days ago   Up 2 days   8050/tcp    metalogo

Docker needs to be installed in the system before run the command. This command will build the Docker image and start a Docker container. You could set a [nginx-proxy](https://github.com/nginx-proxy/nginx-proxy) layer to redirect network requests to MetaLogo container or you can just simply use the MetaLogo docker to recieve outside network traffic from your local network.




