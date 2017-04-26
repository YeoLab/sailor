#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, bcftools, call]

inputs:
  - id: variant_format
    type: string
    default: v
    inputBinding:
      position: 1
      prefix: -O
  - id: use_consensus_caller
    type: boolean
    default: true
    inputBinding: 
      position: 2
      prefix: -c
  - id: call_alts
    type: boolean
    default: true
    inputBinding:
      position: 3
      prefix: -A
  - id: output_vcf
    type: string
    default: intermediateFile.vcf
    inputBinding:
      position: 4
      prefix: -o
#  - id: output_variants_only
#    type: boolean
#    default: true
#    inputBinding:
#      position: 5
#      prefix: -v
  - id: input_gbcf
    type: File
    inputBinding:
      position: 5
outputs:
  - id: output
    type: File
    outputBinding: 
      glob: "*.vcf"
