#!/usr/bin/env cwltool

cwlVersion: v1.0

class: Workflow


inputs:


  input_unsorted_bam:
    type: File

  reference:
    type: File

  known_snp:
    type: File

  single_end:
    type: boolean
    default: true

  reverse_stranded_library:
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

  variants_only:
    type: boolean
    default: true

outputs:


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

  call_snvs_output:
    type: File
    outputSource: call_snvs/output_vcf

  format_variants_output:
    type: File
    outputSource: format_variants/output_vcf

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


  sort:
    run: sort.cwl
    in:
      input_unsorted_bam: input_unsorted_bam
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
      reverse_stranded_library: reverse_stranded_library
    out: [output_bam]

  mpileup:
    run: mpileup.cwl
    in:
      input_bam: filter_reads/output_bam
      reference: reference
    out: [output_gbcf]

  call_snvs:
    run: call_snvs.cwl
    in:
      input_gbcf: mpileup/output_gbcf
    out: [output_vcf]

  format_variants:
    run: format_variants.cwl
    in:
      input_gbcf: call_snvs/output_vcf
      variants_only: variants_only
    out: [output_vcf]

  filter_variants:
    run: filter_variants.cwl
    in:
      input_vcf: format_variants/output_vcf
      min_variant_coverage: min_variant_coverage
      dp: dp
      reverse_stranded_library: reverse_stranded_library
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

