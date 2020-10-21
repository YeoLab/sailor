#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [samtools, calmd]

inputs:

  compressed_bam:
    type: boolean
    default: true
    inputBinding:
      position: 1
      prefix: -b
  # threads:
  #   default: 8
  #   type: int
  #   inputBinding:
  #     position: 2
  #     prefix: --threads
  input_bam:
    type: File
    inputBinding:
      position: 3
  reference:
    type: File
    inputBinding:
      position: 4
      
stdout: $(inputs.input_bam.nameroot)_MD.bam

outputs:

  output_bam:
    type: File
    outputBinding:
      glob: $(inputs.input_bam.nameroot)_MD.bam
