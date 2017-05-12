#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

inputs:

  flags:
    type: int[]

  input_bam:
    type: File

  reference:
    type: File

  known_snp:
    type: File

  single_end:
    type: boolean
    default: true

  junction_overhang:
    type: int
    default: 10

  edge_mutation:
    type: int
    default: 5

  non_ag:
    type: int
    default: 1

  min_variant_coverage:
    type: int
    default: 5

  dp:
    type: string
    default: DP4

  alpha:
    type: int
    default: 0

  beta:
    type: int
    default: 0

  edit_fraction:
    type: float
    default: 0.01

outputs:
  split_bam_output:
    type: File
    outputSource: split/output_bam

  sorted_bam_output:
    type: File
    outputSource: sort/output_bam

  rmdup_bam_output:
    type: File
    outputSource: rmdup/output_bam

  filtered_bam_output:
    type: File
    outputSource: filter_reads/output_bam

  mpileup_output:
    type: File
    outputSource: mpileup/output_gbcf

  call_variants_output:
    type: File
    outputSource: call_variants/output_vcf

  filter_variants_output:
    type: File
    outputSource: filter_variants/output_vcf

  filter_known_snp_output:
    type: File
    outputSource: filter_known_snp/output_vcf

  rank_edits_output:
    type: File
    outputSource: rank_edits/output_conf

steps:

  split:
    run: split_strands.cwl
    in:
      input_bam: input_bam
      flags: flags
    out: [output_bam]

  sort:
    run: sort.cwl
    in:
      input_unsorted_bam: split/output_bam
    out: [output_bam]

  rmdup:
    run: rmdup.cwl
    in:
      single_end: single_end
      duped_bam: sort/output_bam
    out: [output_bam]

  filter_reads:
    run: filter_reads.cwl
    in:
      input_unfiltered_bam: rmdup/output_bam
      junction_overhang: junction_overhang
      edge_mutation: edge_mutation
      non_ag: non_ag
    out: [output_bam]

  mpileup:
    run: mpileup.cwl
    in:
      input_bam: filter_reads/output_bam
      reference: reference
    out: [output_gbcf]

  call_variants:
    run: call_variants.cwl
    in:
      input_gbcf: mpileup/output_gbcf
    out: [output_vcf]

  filter_variants:
    run: filter_variants.cwl
    in:
      input_vcf: call_variants/output_vcf
      min_variant_coverage: min_variant_coverage
      dp: dp
    out: [output_vcf]

  filter_known_snp:
    run: filter_known_snp.cwl
    in:
      input_eff: filter_variants/output_vcf
      known_snp: known_snp
    out: [output_vcf]

  rank_edits:
    run: rank_edits.cwl
    in:
      input_noSNP: filter_known_snp/output_vcf
      edit_fraction: edit_fraction
      alpha: alpha
      beta: beta
    out: [output_conf]