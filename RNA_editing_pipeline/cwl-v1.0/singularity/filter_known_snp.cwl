#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, filter_known_snp.py]
inputs:
  output_noSNP:
    type: string
    default: intermediateFile.noSNP
    inputBinding:
      position: 2
      prefix: -o
  input_eff:
    type: File
    inputBinding:
      position: 1
      prefix: -i
  known_snp:
    type: File
    inputBinding:
      position: 3
      prefix: -k
outputs:
  output:
    type: File
    outputBinding:
      glob: '*.noSNP'

