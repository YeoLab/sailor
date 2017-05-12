#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [split_strands.py]

inputs:

  input_bam:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  reverse_stranded_library:
    type: boolean
    inputBinding:
      position: 2
      prefix: --reverse-strand

arguments: [
  "--output-forward",
  $(inputs.input_bam.nameroot).fwd.bam,
  "--output-reverse",
  $(inputs.input_bam.nameroot).rev.bam
  ]

outputs:

  fwd_output_bam:
    type: File
    format: http://edamontology.org/format_2572
    outputBinding:
      glob: $(inputs.input_bam.nameroot).fwd.bam
    label: ""
    doc: "bam file split on forward flags"
    
  rev_output_bam:
    type: File
    format: http://edamontology.org/format_2572
    outputBinding:
      glob: $(inputs.input_bam.nameroot).rev.bam
    label: ""
    doc: "bam file split on reverse flags"
