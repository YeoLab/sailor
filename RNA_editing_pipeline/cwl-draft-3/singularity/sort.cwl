#!/usr/bin/env cwl-runner
cwlVersion: cwl:draft-3 
class: CommandLineTool 
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, samtools, sort]
inputs:
  - id: input_bam
    type: File
    inputBinding:
      position: 1
  - id: output_bam
    type: string
    default: intermediateFile.sorted.bam
    inputBinding:
      position: 2 
      prefix: -o
outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.output_bam)
