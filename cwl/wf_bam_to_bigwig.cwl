#!/usr/bin/env cwltool

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  
inputs:


  strand:
    type: string

  chrom_sizes:
    type: File
  
  input_bam:
    type: File
    
  split:
    type: boolean
    default: true
    
  bedgraph:
    type: boolean
    default: true


outputs:


  output_bedgraph:
    type: File
    outputSource: step_bam_to_bedgraph/output_bedgraph
  output_sorted_bedgraph:
    type: File
    outputSource: step_sort_bedgraph/output_bedgraph
  output_bigwig:
    type: File
    outputSource: step_bedgraphtobigwig/output


steps:


  step_bam_to_bedgraph:
    run: bam_to_bedgraph.cwl
    in:
      split: split
      strand: strand
      bedgraph: bedgraph
      input_bam: input_bam
    out: [output_bedgraph]
  
  step_rename:
    run: rename.cwl
    in:
      srcfile: step_bam_to_bedgraph/output_bedgraph
      suffix: 
        default: ".bg"
      newname:
        source: [strand, input_bam]
        valueFrom: |
          ${
            if (self[0] == "+") {
              return self[1].nameroot + ".pos"
            }
            else {
              return self[1].nameroot + ".neg"
            }
          }
    out: [outfile]
  step_sort_bedgraph:
    run: sort_bedgraph.cwl
    in:
      input_bedgraph: step_rename/outfile
    out: [output_bedgraph]

  step_bedgraphtobigwig:
    run: bedgraphtobigwig.cwl
    in:
      input_bedgraph: step_sort_bedgraph/output_bedgraph
      chrom_sizes: chrom_sizes
    out: [output]
