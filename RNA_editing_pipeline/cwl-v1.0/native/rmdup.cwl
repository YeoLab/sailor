#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [samtools, rmdup]

inputs:

  duped_bam:
    type: File
    inputBinding:
      position: 1
    label: "duped bam"
    doc: "duped bam"

  single_end:
    type: boolean
    default: true
    inputBinding:
      prefix: -s
      position: 2

  rm_bam:
    type: string
    default: $(inputs.duped_bam.nameroot).rmdup.bam
    inputBinding:
      position: 3

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.input_sort_bam.nameroot).rmdup.bam

