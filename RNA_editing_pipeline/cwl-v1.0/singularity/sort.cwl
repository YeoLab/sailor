#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, samtools,
  sort]
inputs:
  output_bam:
    type: string
    default: intermediateFile.sorted.bam
    inputBinding:
      position: 2
      prefix: -o
  input_bam:
    type: File
    inputBinding:
      position: 1
outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.output_bam)

