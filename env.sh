conda create -n sailor-env -y -c bioconda -c conda-forge \
python=3 \
bedtools \
pybedtools \
pysam \
samtools=1.3 \
bcftools=1.2 \
numpy \
pandas \
scipy \
ucsc-bedgraphtobigwig \
nodejs \
matplotlib \
pybigwig

conda activate sailor-env;

pip install cwltool tqdm gffutils;

cd ./bin && \
  wget https://github.com/byee4/annotator/archive/v0.0.14.tar.gz && \
  cd annotator-0.0.14 && \
  python setup.py install;
