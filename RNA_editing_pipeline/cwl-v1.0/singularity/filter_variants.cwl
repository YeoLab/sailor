#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, filter_variants.py]
inputs:
  min_variant_coverage:
    type: int
    default: 10
    inputBinding:
      position: 3
      prefix: -m
  input_vcf:
    type: File
    inputBinding:
      position: 1
      prefix: -i
  output_vcf:
    type: string
    default: intermediateFile.filtered.vcf
    inputBinding:
      position: 2
      prefix: -o
outputs:
  output:
    type: File
    outputBinding:
      glob: '*.filtered.vcf'

