#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  
baseCommand: [bedGraphToBigWig]

inputs:

  input_bedgraph:
    type: File
    inputBinding:
      position: 1
  chrom_sizes:
    type: File
    inputBinding:
      position: 2
  output_bigwig:
    type: string
    default: ""
    inputBinding:
      position: 3
      valueFrom: |
        ${
          if (inputs.output_bigwig == "") {
            return inputs.input_bedgraph.nameroot + ".bw";
          }
          else {
            return inputs.output_bigwig;
          }
        }

      
outputs:

  output:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.output_bigwig == "") {
            return inputs.input_bedgraph.nameroot + ".bw";
          }
          else {
            return inputs.output_bigwig;
          }
        }


