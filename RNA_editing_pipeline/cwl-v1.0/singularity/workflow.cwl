#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:

  unsorted_bam:
    type: File

  single_end:
    type: boolean
    default: true

  junction_overhang:
    type: int
    default: 10
  edge_mutation:
    type: int
    default: 0
  non_ag:
    type: int
    default: 1

  max_depth:
    type: int
    default: 1000
  calculate_baq:
    type: boolean
    default: true
  reference:
    type: File
  calculate_per_sample:
    type: boolean
    default: true
  tags:
    type: string
    default: DP,DV,DPR,INFO/DPR,DP4,SP
  bcf_format:
    type: boolean
    default: true

  variant_format:
    type: string
    default: v
  use_consensus_caller:
    type: boolean
    default: true
  call_alts:
    type: boolean
    default: true

  filtered_vcf:
    type: string
    default: intermediateFile.filtered.vcf
  min_variant_coverage:
    type: int
    default: 10

  noSNP_eff:
    type: string
    default: intermediateFile.noSNP
  known_snp:
    type: File

  edit_fraction:
    type: float
    default: 0.01
  alpha:
    type: int
    default: 1
  beta:
    type: int
    default: 1

outputs:

  sort_output:
    type: File
    outputSource: sort/output

  rmdup_output:
    type: File
    outputSource: rmdup/output

  filter_reads_output:
    type: File
    outputSource: filter_reads/output

  mpileup_output:
    type: File
    outputSource: mpileup/output

  call_variants_output:
    type: File
    outputSource: call_variants/output

  filter_variants_output:
    type: File
    outputSource: filter_variants/output

  filter_known_output:
    type: File
    outputSource: filter_known/output

  rank_edits_output:
    type: File
    outputSource: rank_edits/output

steps:

  sort:
    run: sort.cwl
    inputs:
    - id: input_bam
      source: unsorted_bam

  rmdup:
    run: rmdup.cwl
    inputs:
    - id: single_end
      source: single_end
    - id: duped_bam
      source: sort/output

  filter_reads:
    run: filter_reads.cwl
    inputs:
    - id: input_bam
      source: rmdup/output
    - id: junction_overhang
      source: junction_overhang
    - id: edge_mutation
      source: edge_mutation
    - id: non_ag
      source: non_ag

  mpileup:
    run: mpileup.cwl
    inputs:
    - id: max_depth
      source: max_depth
    - id: calculate_baq
      source: calculate_baq
    - id: reference
      source: reference
    - id: calculate_per_sample
      source: calculate_per_sample
    - id: tags
      source: tags
    - id: bcf_format
      source: bcf_format
    - id: input_bam
      source: filter_reads/output

  call_variants:
    run: call_variants.cwl
    inputs:
    - id: variant_format
      source: variant_format
    - id: use_consensus_caller
      source: use_consensus_caller
    - id: call_alts
      source: call_alts
    - id: input_gbcf
      source: mpileup/output
  filter_variants:
    run: filter_variants.cwl
    inputs:
    - id: input_vcf
      source: call_variants/output
    - id: output_vcf
      source: filtered_vcf
    - id: min_variant_coverage
      source: min_variant_coverage

  filter_known_snp:
    run: filter_known_snp.cwl
    inputs:
    - id: input_eff
      source: filter_variants/output
    - id: known_snp
      source: known_snp

  rank_edits:
    run: rank_edits.cwl
    inputs:
    - id: input_noSNP
      source: filter_known_snp/output
    - id: edit_fraction
      source: edit_fraction
    - id: alpha
      source: alpha
    - id: beta
      source: beta
