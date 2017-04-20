#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, bcftools, call]

inputs:
  input_gbcf:
    type: File
    inputBinding:
      position: 1
  use_consensus_caller:
    type: boolean
    default: true
    inputBinding:
      position: 2
      prefix: -c
  variant_format:
    type: string
    default: v
    inputBinding:
      position: 3
      prefix: -O
  call_alts:
    type: boolean
    default: true
    inputBinding:
      position: 4
      prefix: -A

arguments: [
  "-o",
  $(inputs.input_gbcf.nameroot).vcf
  ]

outputs:
  output_vcf:
    type: File
    outputBinding:
      glob: $(inputs.input_gbcf.nameroot).vcf

