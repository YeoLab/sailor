#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, samtools,
  rmdup]
inputs:
  duped_bam:
    type: File
    inputBinding:
      position: 1
  single_end:
    type: boolean
    default: true
    inputBinding:
      prefix: -s
      position: 2
  rm_bam:
    type: string
    default: intermediateFile.rmdup.bam
    inputBinding:
      position: 3
outputs:
  output:
    type: File
    outputBinding:
      glob: '*.rmdup.bam'

