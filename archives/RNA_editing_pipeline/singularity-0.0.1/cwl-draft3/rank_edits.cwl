#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, rank_edits.py]
inputs:
  - id: input_noSNP
    type: File
    inputBinding:
      position: 1
      prefix: -i
  - id: output_conf
    type: string
    default: FINALOUTPUT.conf
    inputBinding:
      position: 2
      prefix: -o
  - id: edit_fraction
    type: float
    default: 0.01
    inputBinding:
      position: 3
      prefix: -c
  - id: alpha
    type: int
    default: 0
    inputBinding:
      position: 4
      prefix: -a
  - id: beta
    type: int
    default: 0
    inputBinding:
      position: 5
      prefix: -b
outputs:
  - id: output
    type: File
    outputBinding: 
      glob: "*.conf"
