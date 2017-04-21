#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [split_bams.py]

inputs:

  input_bam:
    type: File
    inputBinding:
      position: 1
      prefix: --input
      
  #flags:
  #  type: int[]
  #  inputBinding:
  #    position: 2
  #    prefix: --flags
  #  default: [1, 2]

arguments: [
  "--flags",
  "1",
  "2",
  "--fwdoutput",
  $(inputs.input_bam.nameroot).fwd.bam,
  "--revoutput",
  $(inputs.input_bam.nameroot).rev.bam
  ]

outputs:

  fwd_output_bam:
    type: File
    format: http://edamontology.org/format_2572
    outputBinding:
      glob: $(inputs.input_bam.nameroot).fwd.bam
    label: ""
    doc: "bam file split on specified flags"
    
  rev_output_bam:
    type: File
    format: http://edamontology.org/format_2572
    outputBinding:
      glob: $(inputs.input_bam.nameroot).rev.bam
    label: ""
    doc: "bam file split on specified flags"
