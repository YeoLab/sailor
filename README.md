RNA Editing

# Installation:

[Install Singularity](http://singularity.lbl.gov/)

[Download Executable](https://s3-us-west-1.amazonaws.com/rnaediting-0.0.2/rnaediting-0.0.2.img)

That's it!

### (Optional) Download Small Example Files:
[Example BAM](https://github.com/YeoLab/rna_editing_pipeline/blob/master/example_data/example.bam)

[Example Reference](https://github.com/YeoLab/rna_editing_pipeline/blob/master/example_data/ce11.chrI.fa)

[Example Known SNPs](https://github.com/YeoLab/rna_editing_pipeline/blob/master/example_data/knownSNPs.bed)

### Download YAML files that describe expt parameters:
[Example YAML](https://github.com/YeoLab/rna_editing_pipeline/blob/master/example_data/example-minimal.yml)

[Example YAML with optional arguments](https://github.com/YeoLab/rna_editing_pipeline/blob/master/example_data/example.yml)
# Running the Pipeline:
```
rnaediting example-minimal.yml
```

### Running the data with optional arguments:

The pipeline only requires 3 arguments: The BAM file, the reference genome, and a list of known SNPs to filter out. Here is the full list and explanation of optional arguments you can provide as needed in the job file:

These are the minimum required arguments needed to run the pipeline (you can see the same information inside the example-minimal.yml file):


This is a BAM file of your reads aligned to the genome. You can generate this file using any short read aligner, and it does not need to be sorted (the pipeline will split + sort things for you). Our example.bam is a downsampled BAM file containing the first 10,000 lines (9,983 reads) of a real sample. 
```YAML
input_bam:
  class: File
  path: example.bam
```

This describes the reference genome in FASTA format (used in the mpileup step), which specifies the reference for which variant reads are compared against. The included reference is the first chromosome of a ce11 assembly.
```YAML
reference:
  class: File
  path: ce11.chrI.fa
```

This file contains a list of known SNPs which will be filtered from the list of candidate editing sites. The example file contains just one SNP in BED3 format (0-based, half-open), which can be used to remove sites that we know aren't editing sites, but are known SNPs.
```YAML
known_snp:
  class: File
  path: knownSNPs.bed
```

This option [true] or false specifies whether or not the reads are single or paired end. This is equivalent to the [-s option](http://www.htslib.org/doc/samtools.html) of ```samtools rmdup``` step, which is part of the workflow.
```YAML
single_end: true
```

This specifies how much overlap is minimally required for a read spanning a junction to be counted. What this really means is when aligned to a reference, if there is a gap between the read (aka spans an intron), we want to ensure there is sufficient overlap in the two sides spanning that gap. See [CIGAR 'N'](https://samtools.github.io/hts-specs/SAMv1.pdf) for more details. 
```YAML
junction_overhang: 10
```

This removes reads with mutations this many nucleotides away from the read. We want to avoid any variations at the read ends where sequencing errors and technical artifacts are more likely to occur. 
```YAML
edge_mutation: 5
```

This specifies the maximum amount of non-AG variations (or TC antisense) we expect per read. If we see multiple AG variants, great! However if we see many unexpected non-AG variants on a per-read basis, we can conservatively remove them from downstream analysis.
```YAML
# remove reads with more than [1] unexpected mutation (one that isn't A-G or T-C antisense).
non_ag: 1
```

This provides a hard filter for variants prior to scoring. By default, for any site to be considered, it must have a total coverage of 5. In this workflow, total coverage is calculated by either the DP flag (specifying coverage), or the 'DP4' flag, specifying "high quality" coverage. This option can be set with the dp: field. See samtools [mpileup](http://www.htslib.org/doc/samtools.html) for more info.
```YAML
min_variant_coverage: 5
dp: DP4
```

These parameters can relax or tighten the beta distribution curve used to score confident editing sites. Increasing the alpha and beta parameters will generally relax coverage requirements, which is sometimes useful for low-coverage data. See the [original paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3959997/) for more info. 
```YAML
alpha: 0
beta: 0
edit_fraction: 0.01
```