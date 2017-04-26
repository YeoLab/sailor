#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, samtools, rmdup]
inputs:
  - id: duped_bam
    type: File
    inputBinding:
      position: 1
  - id: single_end
    type: boolean
    default: true
    inputBinding:
      prefix: -s 
      position: 2
  - id: rm_bam
    type: string
    default: intermediateFile.rmdup.bam
    inputBinding: 
      position: 3
outputs:
  - id: output
    type: File
    outputBinding:
      glob: "*.rmdup.bam"
