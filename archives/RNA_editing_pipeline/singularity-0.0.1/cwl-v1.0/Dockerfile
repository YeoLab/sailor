#################################################################
# Dockerfile
#
# Version:          1
# Software:         RNA Editing Pipeline
# Software Version: 0.0.5
# Description:      Tools for calling RNA editing (A to G) sites
# Website:          http://www.ncbi.nlm.nih.gov/pubmed/24508457
# Tags:             Genomics
# Provides:         samtools 1.3.1, bcftools 1.2, bedtools 2.25.0, numpy 1.11, pandas 0.17, 
# Base Image:       ubuntu:14.04.3
# Build Cmd:        docker build rnae-ubuntu .
# Pull Cmd:         docker pull rnae-ubuntu
# Run Cmd:          docker run rnae-ubuntu
#################################################################

# base image
FROM ubuntu:14.04

################## BEGIN INSTALLATION ###########################

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN wget http://repo.continuum.io/miniconda/Miniconda2-4.1.11-Linux-x86_64.sh  -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm /miniconda.sh && \
    /opt/conda/bin/conda config --set always_yes True --set changeps1 True && \
    /opt/conda/bin/conda update -q conda && \
    /opt/conda/bin/conda info -a


ENV PATH /opt/conda/bin:$PATH

# install

RUN conda install libgfortran
RUN conda install -c bioconda htslib=1.3.1 samtools=1.3.1 bcftools=1.2 bedtools=2.25.0
RUN conda install -c anaconda numpy=1.10 pandas=0.17 scipy=0.16
RUN conda install -c bcbio pybedtools=0.6.9 pysam=0.8.4pre0
RUN conda install -c conda-forge tqdm=4.11.2

# install CWL
pip install cwlref-runner

# addpaths
ADD bin /usr/bin/

# change workdir to /data/
WORKDIR /data/

# set env to the conda environment

ENV PATH="/root/miniconda/bin:$PATH"

# define default command
CMD ["/bin/bash"]

##################### INSTALLATION END ##########################

# File Author / Maintainer
MAINTAINER Brian Yee <bay001@ucsd.edu>

