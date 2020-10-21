#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [filter_reads.py]

inputs:

  input_unfiltered_bam:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  junction_overhang:
    type: int
    default: 10
    inputBinding:
      position: 2
      prefix: --junction_overhang
  edge_mutation:
    type: int
    default: 5
    inputBinding:
      position: 3
      prefix: --edge_mutation
  non_ag:
    type: int
    default: 1
    inputBinding:
      position: 4
      prefix: --non_ag_threshold
  reverse_stranded_library:
    type: boolean
    default: true
    inputBinding:
      position: 5
      prefix: --reverse-strand
  ct:
    type: boolean
    default: false
    inputBinding:
      position: 6
      prefix: --ct
  gt:
    type: boolean
    default: false
    inputBinding:
      position: 6
      prefix: --gt
      
arguments: [
  "--output",
  $(inputs.input_unfiltered_bam.nameroot).readfiltered.bam
]

outputs:

  output_bam:
    type: File
    format: http://edamontology.org/format_2572
    outputBinding:
      glob: $(inputs.input_unfiltered_bam.nameroot).readfiltered.bam
    label: ""
    doc: "filtered bam"
