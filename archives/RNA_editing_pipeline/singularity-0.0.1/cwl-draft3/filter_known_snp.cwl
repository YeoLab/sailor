#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, filter_known_snp.py]

inputs:
  - id: input_eff
    type: File
    inputBinding:
      position: 1
      prefix: -i
  - id: output_noSNP
    type: string
    default: intermediateFile.noSNP
    inputBinding:
      position: 2
      prefix: -o
  - id: known_snp
    type: File
    inputBinding:
      position: 3
      prefix: -k
outputs:
  - id: output
    type: File
    outputBinding: 
      glob: "*.noSNP"
