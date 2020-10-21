#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement

baseCommand: [score_edits_total_coverage.py]

inputs:

  annotated_edits_file:
    type: File
    inputBinding:
      position: 1
      prefix: --annotated_edits_file
  output_filename:
    type: string
    default: ""
    inputBinding:
      position: 1
      prefix: --output_file
      valueFrom: |
        ${
          if (inputs.output_filename == "") {
            return inputs.annotated_edits_file.nameroot + ".editc.tsv";
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
  genome_fa:
    type: File
    inputBinding:
      position: 1
      prefix: --genome_fa
  chrom_sizes_file:
    type: File
    inputBinding:
      position: 1
      prefix: --chrom_sizes_file
  pos_bw:
    type: File
    inputBinding:
      position: 1
      prefix: --pos_bw
  neg_bw:
    type: File
    inputBinding:
      position: 1
      prefix: --neg_bw
      
outputs:

  scored:
    type: File
    outputBinding:
      glob: |
        ${
          if (inputs.output_filename == "") {
            return inputs.annotated_edits_file.nameroot + ".editc.tsv";
          }
          else {
            return inputs.output_filename;
          }
        }
