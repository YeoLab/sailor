#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [bcftools, view]

inputs:
  input_gbcf:
    type: File
    inputBinding:
      position: 1
  types:
    type: string
    default: snps
    inputBinding:
      position: 2
      prefix: -v
  variant_format:
    type: string
    default: v
    inputBinding:
      position: 3
      prefix: -O

arguments: [
  "-o",
  $(inputs.input_gbcf.nameroot).vcf
  ]

outputs:

  output_vcf:
    type: File
    outputBinding:
      glob: $(inputs.input_gbcf.nameroot).vcf

