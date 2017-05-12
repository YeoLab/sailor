#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

# baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, split_bams.py]
baseCommand: [split_bams.py]

inputs:

  input_bam:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  flags:
    type: int[]
    inputBinding:
      position: 2
      prefix: --flags

arguments: [
  "--output",
  $(inputs.input_bam.nameroot).split.bam
  ]

outputs:

  output_bam:
    type: File
    format: http://edamontology.org/format_2572
    outputBinding:
      glob: $(inputs.input_bam.nameroot).split.bam
    label: ""
    doc: "bam file split on specified flags"