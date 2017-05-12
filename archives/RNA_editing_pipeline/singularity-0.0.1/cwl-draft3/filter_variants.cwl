#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, filter_variants.py]

inputs:
  - id: input_vcf
    type: File
    inputBinding:
      position: 1
      prefix: -i
  - id: output_vcf
    type: string
    default: intermediateFile.filtered.vcf
    inputBinding:
      position: 2
      prefix: -o
  - id: min_variant_coverage
    type: int
    default: 10
    inputBinding:
      position: 3
      prefix: -m
outputs:
  - id: output
    type: File
    outputBinding: 
      glob: "*.filtered.vcf"
