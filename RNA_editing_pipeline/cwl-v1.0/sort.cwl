#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

# baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, samtools, sort]
baseCommand: [samtools, sort]

inputs:

  input_unsorted_bam:
    type: File
    format: http://edamontology.org/format_2572
    inputBinding:
      position: 1
    label: "input bam"
    doc: "input bam"

arguments: [
  "-o",
  $(inputs.input_unsorted_bam.nameroot).sorted.bam
  ]

outputs:

  output_bam:
    type: File
    format: http://edamontology.org/format_2572
    outputBinding:
      glob: $(inputs.input_unsorted_bam.nameroot).sorted.bam
    label: ""
    doc: "sorted bam"
    
