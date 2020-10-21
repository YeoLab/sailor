#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [filter_variants.py]

inputs:

  input_vcf:
    type: File
    inputBinding:
      position: 1
      prefix: -i
  min_variant_coverage:
    type: int
    default: 10
    inputBinding:
      position: 2
      prefix: -m
  dp:
    type: string
    inputBinding:
      position: 3
      prefix: --dp
  reverse_split_bam:
    type: boolean
    inputBinding:
      position: 4
      prefix: --reverse-split
  ct:
    type: boolean
    default: false
    inputBinding:
      position: 5
      prefix: --ct
  gt:
    type: boolean
    default: false
    inputBinding:
      position: 5
      prefix: --gt
      
arguments: [
  "-o",
  $(inputs.input_vcf.nameroot).varfiltered.vcf
  ]

outputs:
  output_vcf:
    type: File
    outputBinding:
      glob: $(inputs.input_vcf.nameroot).varfiltered.vcf
