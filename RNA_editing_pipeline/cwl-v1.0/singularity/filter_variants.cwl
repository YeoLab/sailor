#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

baseCommand: [singularity, run, /projects/ps-yeolab/singularity/rnae-ubuntu.img, filter_variants.py]

inputs:
  input_vcf:
    type: File
    inputBinding:
      position: 1
      prefix: -i
  min_variant_coverage:
    type: int
    default: 10
    inputBinding:
      position: 2
      prefix: -m

arguments: [
  "-o",
  $(inputs.input_vcf.nameroot).varfiltered.vcf
  ]

outputs:
  output_vcf:
    type: File
    outputBinding:
      glob: $(inputs.input_vcf.nameroot).varfiltered.vcf