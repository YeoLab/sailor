#!/usr/bin/env cwl-runner

cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, samtools, mpileup]

inputs:
  - id: max_depth
    type: int
    default: 1000
    inputBinding:
      position: 1
      prefix: -d
  - id: calculate_baq
    type: boolean
    default: true
    inputBinding: 
      position: 2
      prefix: -E
  - id: reference
    type: File
    inputBinding:
      position: 3
      prefix: -f
  - id: calculate_per_sample
    type: boolean
    default: true
    inputBinding:
      position: 4
      prefix: -p
  - id: tags
    type: string
    default: DP,DV,DPR,INFO/DPR,DP4,SP
    inputBinding:
      position: 5
      prefix: -t
  - id: bcf_format
    type: boolean
    default: true
    inputBinding:
      position: 6
      prefix: -g
  - id: input_bam
    type: File
    inputBinding: 
      position: 7
      prefix: -I
  - id: output_gbcf
    type: string
    default: intermediateFile.gbcf
    inputBinding:
      position: 8
      prefix: -o
outputs:
  - id: output
    type: File
    outputBinding: 
      glob: "*.gbcf"
