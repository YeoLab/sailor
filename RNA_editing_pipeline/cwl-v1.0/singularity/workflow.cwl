#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
- id: unsorted_bam
  type: File
- id: sorted_bam
  type: string
  default: intermediateFile.sorted.bam
- id: single_end
  type: boolean
  default: true
- id: rmdup_sorted_bam
  type: string
  default: intermediateFile.rmdup.bam
- id: filtered_bam
  type: string
  default: intermediateFile.filtered.bam
- id: junction_overhang
  type: int
  default: 10
- id: edge_mutation
  type: int
  default: 0
- id: non_ag
  type: int
  default: 1
- id: max_depth
  type: int
  default: 1000
- id: calculate_baq
  type: boolean
  default: true
- id: reference
  type: File
- id: calculate_per_sample
  type: boolean
  default: true
- id: tags
  type: string
  default: DP,DV,DPR,INFO/DPR,DP4,SP
- id: bcf_format
  type: boolean
  default: true
- id: output_gbcf
  type: string
  default: intermediateFile.gbcf
- id: variant_format
  type: string
  default: v
- id: use_consensus_caller
  type: boolean
  default: true
- id: call_alts
  type: boolean
  default: true
- id: output_vcf
  type: string
  default: intermediateFile.vcf
- id: filtered_vcf
  type: string
  default: intermediateFile.filtered.vcf
- id: min_variant_coverage
  type: int
  default: 10
- id: noSNP_eff
  type: string
  default: intermediateFile.noSNP
- id: known_snp
  type: File
- id: output_conf
  type: string
  default: FINALOUTPUT.conf
- id: edit_fraction
  type: float
  default: 0.01
- id: alpha
  type: int
  default: 0
- id: beta
  type: int
  default: 0 

outputs:
- id: sorted_output
  type: File
  outputSource: '#sort/output'
- id: rmdup_output
  type: File
  outputSource: '#rmdup/output'
- id: filter_reads_output
  type: File
  outputSource: '#filter_reads/output'
- id: mpileup_output
  type: File
  outputSource: '#mpileup/output'
- id: call_variants_output
  type: File
  outputSource: '#call_variants/output'
- id: filter_variants_output
  type: File
  outputSource: '#filter_variants/output'
- id: filter_known_output
  type: File
  outputSource: '#filter_known_snp/output'
- id: ranked_output
  type: File
  outputSource: '#rank_edits/output'
steps:
- id: sort
  run: sort.cwl
  inputs:
  - id: input_bam
    source: '#unsorted_bam'
  - id: output_bam
    source: '#sorted_bam'
  outputs:
  - id: output
- id: rmdup
  run: rmdup.cwl
  inputs:
  - id: single_end
    source: '#single_end'
  - id: duped_bam
    source: '#sort/output'
  - id: rm_bam
    source: '#rmdup_sorted_bam'
  outputs:
  - id: output
- id: filter_reads
  run: filter_reads.cwl
  inputs:
  - id: input_bam
    source: '#rmdup/output'
  - id: output_bam
    source: '#filtered_bam'
  - id: junction_overhang
    source: '#junction_overhang'
  - id: edge_mutation
    source: '#edge_mutation'
  - id: non_ag
    source: '#non_ag'
  outputs:
  - id: output
- id: mpileup
  run: mpileup.cwl
  inputs:
  - id: max_depth
    source: '#max_depth'
  - id: calculate_baq
    source: '#calculate_baq'
  - id: reference
    source: '#reference'
  - id: calculate_per_sample
    source: '#calculate_per_sample'
  - id: tags
    source: '#tags'
  - id: bcf_format
    source: '#bcf_format'
  - id: input_bam
    source: '#filter_reads/output'
  - id: output_gbcf
    source: '#output_gbcf'
  outputs:
  - id: output
- id: call_variants
  run: call_variants.cwl
  inputs:
  - id: variant_format
    source: '#variant_format'
  - id: use_consensus_caller
    source: '#use_consensus_caller'
  - id: call_alts
    source: '#call_alts'
  - id: output_vcf
    source: '#output_vcf'
  - id: input_gbcf
    source: '#mpileup/output'
  outputs:
  - id: output
- id: filter_variants
  run: filter_variants.cwl
  inputs:
  - id: input_vcf
    source: '#call_variants/output'
  - id: output_vcf
    source: '#filtered_vcf'
  - id: min_variant_coverage
    source: '#min_variant_coverage'
  outputs:
  - id: output
- id: filter_known_snp
  run: filter_known_snp.cwl
  inputs:
  - id: input_eff
    source: '#filter_variants/output'
  - id: output_noSNP
    source: '#noSNP_eff'
  - id: known_snp
    source: '#known_snp'
  outputs:
  - id: output
- id: rank_edits
  run: rank_edits.cwl
  inputs:
  - id: input_noSNP
    source: '#filter_known_snp/output'
  - id: output_conf
    source: '#output_conf'
  - id: edit_fraction
    source: '#edit_fraction'
  - id: alpha
    source: '#alpha'
  - id: beta
    source: '#beta'
  outputs:
  - id: output

