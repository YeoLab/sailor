#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, samtools,
  mpileup]
inputs:
  calculate_per_sample:
    type: boolean
    default: true
    inputBinding:
      position: 4
      prefix: -p
  reference:
    type: File
    inputBinding:
      position: 3
      prefix: -f
  tags:
    type: string
    default: DP,DV,DPR,INFO/DPR,DP4,SP
    inputBinding:
      position: 5
      prefix: -t
  output_gbcf:
    type: string
    default: intermediateFile.gbcf
    inputBinding:
      position: 8
      prefix: -o
  calculate_baq:
    type: boolean
    default: true
    inputBinding:
      position: 2
      prefix: -E
  input_bam:
    type: File
    inputBinding:
      position: 7
      prefix: -I
  max_depth:
    type: int
    default: 1000
    inputBinding:
      position: 1
      prefix: -d
  bcf_format:
    type: boolean
    default: true
    inputBinding:
      position: 6
      prefix: -g
outputs:
  output:
    type: File
    outputBinding:
      glob: '*.gbcf'

