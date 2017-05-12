#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

# baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, filter_reads.py]
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