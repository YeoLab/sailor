#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [filter_reads.py]

inputs:
  input_bam:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  output_bam:
    type: string
    default: intermediateFile.filtered.bam
    inputBinding:
      position: 2
      prefix: --output
  junction_overhang:
    type: int
    default: 10
    inputBinding:
      position: 3
      prefix: --junction_overhang
  edge_mutation:
    type: int
    default: 0
    inputBinding:
      position: 4
      prefix: --edge_mutation
  non_ag:
    type: int
    default: 1
    inputBinding:
      position: 5
      prefix: --non_ag_threshold

outputs:
  output:
    type: File
    outputBinding:
      glob $(inputs.input_bam.nameroot).filtered.bam
