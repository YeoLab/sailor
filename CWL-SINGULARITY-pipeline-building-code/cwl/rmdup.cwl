#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [ifnotskip]

arguments: [samtools, rmdup]


inputs:

  skip_duplicate_removal:
     type: boolean
     default: false
     inputBinding:
       position: -1
       prefix: --skip

  duped_bam:
    type: File
    inputBinding:
      position: 1
    label: "duped bam"
    doc: "duped bam"

  rm_bam:
    type: string
    default: rmduped.bam
    inputBinding:
      position: 2
      valueFrom: $(inputs.duped_bam.nameroot).rmdup.bam

  single_end:
    type: boolean
    default: true
    inputBinding:
      prefix: -s
      position: 3

       
outputs:

  output_bam:
    type: File
    outputBinding:
      glob: $(inputs.duped_bam.nameroot).rmdup.bam
