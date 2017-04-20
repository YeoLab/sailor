#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [filter_known_snp.py]

inputs:
  input_eff:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  known_snp:
    type: File
    inputBinding:
      position: 2
      prefix: --known

arguments: [
  "--output",
  $(inputs.input_eff.nameroot).snpfiltered.vcf
  ]

outputs:
  output_vcf:
    type: File
    outputBinding:
      glob: $(inputs.input_eff.nameroot).snpfiltered.vcf
