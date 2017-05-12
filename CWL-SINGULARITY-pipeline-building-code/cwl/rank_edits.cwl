#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [rank_edits.py]

inputs:

  input_noSNP:
    type: File
    inputBinding:
      position: 1
      prefix: -i
  edit_fraction:
    type: float
    default: 0.01
    inputBinding:
      position: 2
      prefix: -c
  alpha:
    type: int
    default: 0
    inputBinding:
      position: 3
      prefix: -a
  beta:
    type: int
    default: 0
    inputBinding:
      position: 4
      prefix: -b
  keep_all_edited:
    type: boolean
    default: false
    inputBinding:
      position: 5
      prefix: --keep-100-edited

arguments: [
  "--output",
  $(inputs.input_noSNP.nameroot).ranked.conf
  ]

outputs:

  output_conf:
    type: File
    outputBinding:
      glob: $(inputs.input_noSNP.nameroot).ranked.conf
  output_bed:
    type: File
    outputBinding:
      glob: $(inputs.input_noSNP.nameroot).ranked.bed
  # output_vcf:
  #   type: File
  #   outputBinding:
  #     glob: $(inputs.input_noSNP.nameroot).ranked.vcf