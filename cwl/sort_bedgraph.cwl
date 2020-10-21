#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool


baseCommand: [bedtools, sort]

inputs:

  input_bedgraph:
    type: File
    inputBinding:
      position: 1
      prefix: -i

stdout: $(inputs.input_bedgraph.nameroot).sorted.bg

outputs:

  output_bedgraph:
    type: File
    outputBinding:
      glob: $(inputs.input_bedgraph.nameroot).sorted.bg

