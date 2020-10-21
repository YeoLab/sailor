#!/usr/bin/env cwltool

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

baseCommand: [combine_and_reformat.py]

inputs:
  forward_edits:
    type: File
    inputBinding:
      position: 1
      prefix: --fwd
  reverse_edits:
    type: File
    inputBinding:
      position: 2
      prefix: --rev
  output_filename:
    type: string
    default: ""
    inputBinding:
      position: 2
      prefix: --output
      valueFrom: |
        ${
          if (inputs.output_filename == "") {
            return inputs.forward_edits.basename.replace(".fwd",".combined");
          }
          else {
            return inputs.output_filename;
          }
        }
  force_overwrite:
    type: boolean
    default: true
    inputBinding:
      position: 3
      prefix: --force
      
outputs:

  output_combined_bed:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.output_filename == "") {
            return inputs.forward_edits.basename.replace(".fwd",".combined");
          }
          else {
            return inputs.output_filename;
          }
        }