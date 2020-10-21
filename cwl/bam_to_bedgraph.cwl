#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

baseCommand: [bedtools, genomecov]

inputs:

  split:
    type: boolean
    default: true
    inputBinding:
      position: 1
      prefix: -split
  strand:
    type: string
    inputBinding:
      position: 1
      prefix: -strand
  bedgraph:
    type: boolean
    inputBinding:
      position: 1
      prefix: -bg
  input_bam:
    type: File
    inputBinding:
      position: 1
      prefix: -ibam
    
outputs:

  output_bedgraph:
    type: stdout
    
