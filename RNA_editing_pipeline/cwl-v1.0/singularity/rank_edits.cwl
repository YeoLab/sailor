#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, rank_edits.py]
inputs:
  input_noSNP:
    type: File
    inputBinding:
      position: 1
      prefix: -i
  edit_fraction:
    type: float
    default: 0.01
    inputBinding:
      position: 3
      prefix: -c
  alpha:
    type: int
    default: 0
    inputBinding:
      position: 4
      prefix: -a
  beta:
    type: int
    default: 0
    inputBinding:
      position: 5
      prefix: -b
  output_conf:
    type: string
    default: FINALOUTPUT.conf
    inputBinding:
      position: 2
      prefix: -o
outputs:
  output:
    type: File
    outputBinding:
      glob: '*.conf'

