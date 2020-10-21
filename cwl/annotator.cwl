#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

baseCommand: [annotator]

inputs:

  input_bed:
    type: File
    inputBinding:
      position: 1
      prefix: --input
  output_filename:
    type: string
    default: ""
    inputBinding:
      position: 1
      prefix: --output
      valueFrom: |
        ${
          if (inputs.output_filename == "") {
            return inputs.input_bed.nameroot + ".annotated";
          }
          else {
            return inputs.output_filename;
          }
        }

  gtfdb:
    type: File
    inputBinding:
      position: 1
      prefix: --gtfdb
  species:
    type: string
    inputBinding:
      position: 1
      prefix: --species
    
outputs:

  annotated:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.output_filename == "") {
            return inputs.input_bed.nameroot + ".annotated";
          }
          else {
            return inputs.output_filename;
          }
        }

    
