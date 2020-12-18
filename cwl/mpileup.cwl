#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [samtools, mpileup]

inputs:

  max_depth:
    type: int
    default: 100000000
    inputBinding:
      position: 1
      prefix: -d
  calculate_baq:
    type: boolean
    default: true
    inputBinding:
      position: 2
      prefix: -E
  reference:
    type: File
    inputBinding:
      position: 3
      prefix: -f
  calculate_per_sample:
    type: boolean
    default: true
    inputBinding:
      position: 4
      prefix: -p
  tags:
    type: string
    default: DP,DV,DPR,INFO/DPR,DP4,SP
    inputBinding:
      position: 5
      prefix: -t
  bcf_format:
    type: boolean
    default: true
    inputBinding:
      position: 6
      prefix: -g
  input_bam:
    type: File
    inputBinding:
      position: 7
      prefix: -I

arguments: [
  "-o",
  $(inputs.input_bam.nameroot).gbcf
  ]

outputs:

  output_gbcf:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.nameroot).gbcf
