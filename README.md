![logo](https://github.com/YeoLab/rna_editing_pipeline/blob/master/logo/sailor-logo.png)

### Note: Current changes to master may be unstable! Use the frozen singularity file to reproduce paper results.
### Note # 2: You should check whether your aligner provides the MD tag, as this is necessary to determine the non A/G mismatches between the reference and query.

# Software for Accurately Identifying Locations Of RNA-editing (SAILOR)

SAILOR implements published methodologies to assess adenosine to inosine changes in RNA-SEQ data for easy identification of transcriptome-wide editing. 
The SAILOR pipeline is available as both a [CWL workflow](http://www.commonwl.org) and as a [Singularity container](http://singularity.lbl.gov) and is designed for ease of use to run with one command. 
It requires a [BAM](https://genome.ucsc.edu/FAQ/FAQformat.html#format5.1)-formatted file of the sequence alignments, a [FASTA](http://genetics.bwh.harvard.edu/pph/FASTA.html)-formatted reference genome sequence (of any organism or cell-type), 
and a [BED3](https://genome.ucsc.edu/FAQ/FAQformat.html#format1)-formatted file of known SNPs. SAILOR allows the user to specify a range of filtering criteria including: Non A-to-I mismatch rate, 
location of mismatches (to account for biases at the end of reads), and a minimum read coverage required to call variants. Users may relax any 
of these filtering criteria and/or pursue analysis of A-to-I editing sites with lower confidence scores.

# Installation:

[Install singularity](http://singularity.lbl.gov/install-linux)

[Download executable into an empty directory](https://s3-us-west-1.amazonaws.com/sailor-1.0.4/sailor-1.0.4)

That's it!

# Running the Pipeline:

Mark downloaded programme as executable:
```
chmod +x sailor-1.0.4
```

Display  a brief overview of options and expected parameters:
```
./sailor-1.0.4
```
Type 'y' to populate the current folder with example files:

```
Do you want me to copy now into your current directory an example of data input files and a job template (y/-):y
```

Execute the analysis using the provided example YAML file pointing to the appropriate bundled example files
```
./sailor-1.0.4 ce11_example.yaml
```

### Running the data with required arguments:

Running time for the examples should be quick! Running on a complete dataset takes a few hours for C elegans data, 
so sit back and relax by reading the rest of this README.

These are the minimum required arguments needed to run the pipeline (you can view the same information inside the example.yml file):


This is a BAM file ([Example](https://github.com/YeoLab/sailor/blob/master/CWL-SINGULARITY-pipeline-building-code/example/ce11_example_single_end.bam)) of your reads aligned to the genome. You can generate this file using any short read aligner, and it does not need to be sorted (the pipeline will split + sort things for you). **Note: You should check whether your aligner provides the MD tag, as this is necessary to determine the non A/G mismatches between the reference and query.** Our example.bam is a downsampled BAM file containing the first 10,000 lines (9,983 reads) of a real sample:
```YAML
input_bam:
  class: File
  path: ce11_example_single_end.bam
```


This describes the reference genome in FASTA format ([Example](https://github.com/YeoLab/sailor/blob/master/CWL-SINGULARITY-pipeline-building-code/example/ce11.chrI.fa)) (used in the mpileup step), which specifies the reference for which variant reads are compared against. The included reference is the first chromosome of a ce11 assembly:
```YAML
reference:
  class: File
  path: ce11.chrI.fa
```


This file contains a list of known SNPs ([Example](https://github.com/YeoLab/sailor/blob/master/CWL-SINGULARITY-pipeline-building-code/example/ce11_known_SNPs.bed)) which will be filtered from the list of candidate editing sites. The example file contains just one SNP in BED3 format (0-based, half-open), which can be used to remove sites that we know aren't editing sites, but are known SNPs:
```YAML
known_snp:
  class: File
  path: ce11_known_SNPs.bed
```


### Running the data with optional arguments:

The pipeline only requires 3 arguments: The BAM file, the reference genome, and a list of known SNPs to filter out. 
If you find that using default parameters are not fit to your data, you may want to play around with the optional arguments. 
Here is the full list and explanation of optional arguments you can provide as needed in the job file 
(You can find an example YAML configuaration file [here](https://github.com/YeoLab/sailor/blob/master/CWL-SINGULARITY-pipeline-building-code/example/ce11_example.yaml)):

This parameter [true] or false specifies whether or not we're dealing with a reversely stranded library:
```YAML
reverse_stranded_library: true
```

This option [true] or false specifies whether or not the reads are single or paired end. This is equivalent to the [-s option](http://www.htslib.org/doc/samtools.html) of ```samtools rmdup``` step, which is part of the workflow. However, each read will still be split according to strand which will affect paired-end reads oriented opposite each other:
```YAML
single_end: true
```

This specifies how much overlap is minimally required for a read spanning a junction to be counted. What this really means is when aligned to a reference, if there is a gap between the read (aka spans an intron), we want to ensure there is sufficient overlap in the two sides spanning that gap. See [CIGAR 'N'](https://samtools.github.io/hts-specs/SAMv1.pdf) for more details:
```YAML
junction_overhang: 10
```

This removes reads with mutations this many nucleotides away from the read. We want to avoid any variations at the read ends where sequencing errors and technical artifacts are more likely to occur:
```YAML
edge_mutation: 5
```

This specifies the maximum amount of non-AG variations (or TC antisense) we expect per read. If we see multiple AG variants, great! However if we see many unexpected non-AG variants on a per-read basis, we can conservatively remove them from downstream analysis:
```YAML
# remove reads with more than [1] unexpected mutation (one that isn't A-G or T-C antisense).
non_ag: 1
```

This provides a hard filter for variants prior to scoring. By default, for any site to be considered, it must have a total coverage of 5. In this workflow, total coverage is calculated by either the DP flag (specifying coverage), or the 'DP4' flag, specifying "high quality" coverage. This option can be set with the dp: field. See samtools [mpileup](http://www.htslib.org/doc/samtools.html) for more info:
```YAML
min_variant_coverage: 5
dp: DP4
```

These parameters can relax or tighten the beta distribution curve used to score confident editing sites. Essentially these numbers adjust the pseudocount added to variant site coverage. Therefore increasing the alpha and beta parameters will generally relax coverage requirements, which is sometimes useful for low-coverage data. See the [original paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3959997/) for more info:
```YAML
alpha: 0
beta: 0
edit_fraction: 0.01
```

This parameter specifies options to either 1) keep 100% edited sites as confident 'edited' sites (true), or 2) flag as 'possible snps' (false):
```YAML
keep_all_edited: false
```

This parameter specifies whether or not you want to skip the 'samtools rmdup' step of the pipeline:
```YAML
skip_duplicate_removal: false
```

# Outputs:
There are lots of intermediate files, but the ones we want are the bed files (it's a long name, but it helps trace all the steps and filters that the pipeline goes through):
```
SAMPLENAME.fwd.sorted.rmdup.readfiltered.formatted.varfiltered.snpfiltered.ranked.bed
SAMPLENAME.rev.sorted.rmdup.readfiltered.formatted.varfiltered.snpfiltered.ranked.bed
```
These BED6 files correspond to candidate editing sites found at either the positive strand (fwd) or negative strand (rev):

### Format of the BED file:

1. chromosome
2. start (0-based) index of an editing site
3. end (open) index of an editing site
4. unique name containing information about coverage|variant type|edit% (```84|A>G|0.011904762``` corresponds to an A>G (+) site covered by 84 reads that is ~1% edited)
5. confidence score
6. strand

You can load these BED files onto [IGV](http://software.broadinstitute.org/software/igv/download) and see if your gene of interest is edited.
For a more global viewpoint, you will need to filter this BED file based on the 'confidence score' (tab 5) using anything that can sort/filter a tabbed file. Then you can look at these filtered sites on IGV.

If you don't see many sites, you can relax the parameters, or look into the intermediate files described below:

If our sample is ```sample.bam```, we expect to obtain a list of the following outputs (for both fwd and rev stranded edits):


sorted BAM file:

```
example.fwd.sorted.bam
```


sorted BAM file with 'duplicate reads' removed (defined as reads sharing the same external mapped coordinates, keeping reads with the highest mapping quality (see [samtools](http://www.htslib.org/doc/samtools.html)):

```
example.fwd.sorted.rmdup.bam
```


The above BAM file filtered of reads that do not pass read-centric thresholds:

```
example.fwd.sorted.rmdup.readfiltered.bam
```


The above BAM file as pileup in gbcf (binary) format:

```
example.fwd.sorted.rmdup.readfiltered.gbcf
```


The above gbcf file in human-readable vcf format:

```
example.fwd.sorted.rmdup.readfiltered.vcf
```


The above vcf file in a more familiar vcf format:

```
example.fwd.sorted.rmdup.readfiltered.formatted.vcf
```


The above vcf file filtered of SNVs that do not pass the position-centric thresholds:

```
example.fwd.sorted.rmdup.readfiltered.formatted.varfiltered.vcf
```


The above vcf file filtered of SNVs that are also known SNPs:

```
example.fwd.sorted.rmdup.readfiltered.formatted.varfiltered.snpfiltered.vcf
```


The above vcf file in a tabular 'confidence' format, showing:

```
example.fwd.sorted.rmdup.readfiltered.formatted.varfiltered.snpfiltered.ranked.conf
```

##### Format (tabs) of the conf file:
1. (#CHROM) : chromosome
2. (POS) : 1-based position of the editing site
3. (NUM_READS) : number of total coverage
4. (REF) : reference allele
5. (ALT) : alternate allele
6. (CONFIDENCE) : confidence score
7. (POST_PSEUDOCOUNT_EDIT%) : if we add pseudocounts, the edit % will be here
8. (PRE_PSEUDOCOUNT_EDIT%) : native edit %
9. (FILTER) : either PASS for a valid editing candidate (regardless of score), or SNP if the site was 100% A>G
10. (INFO) : vcf "info" column (see [vcf](https://samtools.github.io/hts-specs/VCFv4.2.pdf) format for details)
11. (GENOTYPE) : vcf "genotype" column
12. (baz) : vcf "genotype value" column


## Other notes.

If using python3.8, you might run into a warning related to buffer size (ie. 

```bash
subprocess.py:849: RuntimeWarning: line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used
```

)

This was identified here and doesn't appear to affect this pipeline.

https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=954388

##

# References:

Washburn, M. C., Kakaradov, B., Sundararaman, B., Wheeler, E., Hoon, S., Yeo, G. W., & Hundley, H. A. (2014): The dsRBP and inactive editor ADR-1 utilizes dsRNA binding to regulate A-to-I RNA editing across the C. elegans transcriptome. 
Cell reports, 6(4), 599-607.

Amstutz, Peter; Crusoe, Michael R.; Tijanić, Nebojša; Chapman, Brad; Chilton, John; Heuer, Michael; Kartashov, Andrey; Leehr, Dan; Ménager, Hervé; Nedeljkovich, Maya; Scales, Matt; Soiland-Reyes, Stian; Stojanovic, Luka (2016): Common Workflow Language, v1.0. 
figshare. https://doi.org/10.6084/m9.figshare.3115156.v2
Retrieved: 22 13, May 11, 2017 (GMT)

Kurtzer GM, Sochat V, Bauer MW (2017): Singularity: Scientific containers for mobility of compute. 
PLoS ONE 12(5): e0177459. https://doi.org/10.1371/journal.pone.0177459

