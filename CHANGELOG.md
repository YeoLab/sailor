# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).



## [1.0.4] - 5-12-2017
### Added
- added ...

### Changed
- changed ...

### Removed
- removed ...

### Fixed
- fixed paths in README

## [0.0.3DEV] - 5-4-2017
### Added
- BED file outputs to replace conf file as the final output

### Changed
- changed the 'reverse-strand' flag in filter_variants.py to '--reverse-split'. --reverse-split is true if the pipeline deals with '*.rev.bam' files generated from step1.

### Removed
- removed reverse-strand flags for filter_variants.py : we now get strand information based on how the mapped reads were split in the beginning of the workflow.

### Fixed
- changing the reverse flag in filter_variants now fixes instances where A-G changes were being called falsely on Paired End reads mapped to the reverse gene.


## [0.0.3DEV] - 5-9-2017
### Added
- example yaml files for PE and SE
- keep-100-edited flag to the 'rank_edits.py' script to keep or discard 100% edited SNVs

### Changed
- changed ...

### Removed
- removed ...

### Fixed
- fixed paths in README

## [0.0.3DEV] - 5-4-2017
### Added
- BED file outputs to replace conf file as the final output

### Changed
- changed the 'reverse-strand' flag in filter_variants.py to '--reverse-split'. --reverse-split is true if the pipeline deals with '*.rev.bam' files generated from step1.

### Removed
- removed reverse-strand flags for filter_variants.py : we now get strand information based on how the mapped reads were split in the beginning of the workflow.

### Fixed
- changing the reverse flag in filter_variants now fixes instances where A-G changes were being called falsely on Paired End reads mapped to the reverse gene.

## [0.0.3DEV] - 5-1-2017
### Added
- reverse-strand flags for:
  - filter_reads.py
  - filter_variants.py
  - split_strands.py
- new test_cases for filter_reads
- new test_cases for filter_variants
- new test_cases for split_strands
- example runscripts and job files to 0.0.3DEV versions for PE

### Changed
- cwl tools now reflect and have the option for reverse strand libraries (untested for forward)
- moved complete single-end example example_outputs folder
- added PE example data
- changed 'fwd' in reverse strand libraries to output A-G editing sites, and 'rev' in reverse strand libraries to output T-C (previously the opposite).

### Removed
- removed ...

### Fixed
- get_junction_overhangs() now checks for multiple junctions per read (ie. 34M10N34M10N34M)

## [0.0.3DEV] - 2017-04-27
### Added
- example runscripts and job files 0.0.3DEV versions
- example input and output files to 0.0.2

### Changed
- moved cwl-1.0 and cwl-draft3 to 'singularity-0.0.1'
- added a better README file

### Removed
- removed ...

### Fixed
- fixed ...

## [0.0.2] - 2017-03-04
### Added
- example runscripts and job files 0.0.2 versions
- example input and output files to 0.0.2

### Changed
- changed ...

### Removed
- removed ...

### Fixed
- fixed ...
