#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, bcftools,
  call]
inputs:
  use_consensus_caller:
    type: boolean
    default: true
    inputBinding:
      position: 2
      prefix: -c
  input_gbcf:
#  - id: output_variants_only
#    type: boolean
#    default: true
#    inputBinding:
#      position: 5
#      prefix: -v
    type: File
    inputBinding:
      position: 5
  variant_format:
    type: string
    default: v
    inputBinding:
      position: 1
      prefix: -O
  call_alts:
    type: boolean
    default: true
    inputBinding:
      position: 3
      prefix: -A
  output_vcf:
    type: string
    default: intermediateFile.vcf
    inputBinding:
      position: 4
      prefix: -o
outputs:
  output:
    type: File
    outputBinding:
      glob: '*.vcf'

