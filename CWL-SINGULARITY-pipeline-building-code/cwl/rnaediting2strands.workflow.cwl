#!/usr/bin/env cwltool

cwlVersion: v1.0

class: Workflow


requirements:
  - class: SubworkflowFeatureRequirement


inputs:

  input_bam:
    type: File

  reference:
    type: File

  known_snp:
    type: File

  reverse_stranded_library:
    type: boolean
    default: true

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

  keep_all_edited:
    type: boolean
    default: false
  
  ct:
    type: boolean
    default: false
  gt:
    type: boolean
    default: false
    
### These shouldn't change at all. I just need to ensure ###
### the forward/reverse flags are explicitly set ###

  fwd_is_reverse:
    type: boolean
    default: false

  rev_is_reverse:
    type: boolean
    default: true

  skip_duplicate_removal:
    type: boolean
    default: false

outputs:


  fwd_sorted_bam_output:
    type: File
    outputSource: fwd/sorted_bam_output

  fwd_rmdup_bam_output:
    type: File
    outputSource: fwd/rmdup_bam_output

  fwd_filtered_bam_output:
    type: File
    outputSource: fwd/filtered_bam_output

  fwd_mpileup_output:
    type: File
    outputSource: fwd/mpileup_output

  fwd_call_snvs_output:
    type: File
    outputSource: fwd/call_snvs_output

  fwd_format_variants_output:
    type: File
    outputSource: fwd/format_variants_output

  fwd_filter_variants_output:
    type: File
    outputSource: fwd/filter_variants_output

  fwd_filter_known_snp_output:
    type: File
    outputSource: fwd/filter_known_snp_output

  fwd_rank_edits_output:
    type: File
    outputSource: fwd/rank_edits_output

  fwd_rank_edits_output_bed:
    type: File
    outputSource: fwd/rank_edits_output_bed

  # fwd_rank_edits_output_vcf:
  #   type: File
  #   outputSource: fwd/rank_edits_output_vcf

  rev_sorted_bam_output:
    type: File
    outputSource: rev/sorted_bam_output

  rev_rmdup_bam_output:
    type: File
    outputSource: rev/rmdup_bam_output

  rev_filtered_bam_output:
    type: File
    outputSource: rev/filtered_bam_output

  rev_mpileup_output:
    type: File
    outputSource: rev/mpileup_output

  rev_call_snvs_output:
    type: File
    outputSource: rev/call_snvs_output

  rev_format_variants_output:
    type: File
    outputSource: rev/format_variants_output

  rev_filter_variants_output:
    type: File
    outputSource: rev/filter_variants_output

  rev_filter_known_snp_output:
    type: File
    outputSource: rev/filter_known_snp_output

  rev_rank_edits_output:
    type: File
    outputSource: rev/rank_edits_output

  rev_rank_edits_output_bed:
    type: File
    outputSource: rev/rank_edits_output_bed

  # rev_rank_edits_output_vcf:
  #   type: File
  #   outputSource: rev/rank_edits_output_vcf

steps:

  split_strands:
    run: split_strands.cwl
    in:
      input_bam: input_bam
      reverse_stranded_library: reverse_stranded_library
    out: [fwd_output_bam, rev_output_bam]
    
  fwd:
    run: rnaediting1strand.cwl
    in: 
      input_unsorted_bam: split_strands/fwd_output_bam
      known_snp: known_snp
      reference: reference
      single_end: single_end
      reverse_stranded_library: reverse_stranded_library
      reverse_split_bam: fwd_is_reverse
      junction_overhang: junction_overhang
      edge_mutation: edge_mutation
      non_ag: non_ag
      min_variant_coverage: min_variant_coverage
      dp: dp
      alpha: alpha
      beta: beta
      edit_fraction: edit_fraction
      keep_all_edited: keep_all_edited
      skip_duplicate_removal: skip_duplicate_removal
      ct: ct
      gt: gt
    out:
      # [sorted_bam_output, rmdup_bam_output, filtered_bam_output, mpileup_output, call_snvs_output, format_variants_output, filter_variants_output, filter_known_snp_output, rank_edits_output, rank_edits_output_vcf, rank_edits_output_bed]
      [sorted_bam_output, rmdup_bam_output, filtered_bam_output, mpileup_output, call_snvs_output, format_variants_output, filter_variants_output, filter_known_snp_output, rank_edits_output, rank_edits_output_bed]

  rev:
    run: rnaediting1strand.cwl
    in: 
      input_unsorted_bam: split_strands/rev_output_bam
      known_snp: known_snp
      reference: reference
      single_end: single_end
      reverse_stranded_library: reverse_stranded_library
      reverse_split_bam: rev_is_reverse
      junction_overhang: junction_overhang
      edge_mutation: edge_mutation
      non_ag: non_ag
      min_variant_coverage: min_variant_coverage
      dp: dp
      alpha: alpha
      beta: beta
      edit_fraction: edit_fraction
      keep_all_edited: keep_all_edited
      skip_duplicate_removal: skip_duplicate_removal
      ct: ct
      gt: gt
    out:
      # [sorted_bam_output, rmdup_bam_output, filtered_bam_output, mpileup_output, call_snvs_output, format_variants_output, filter_variants_output, filter_known_snp_output, rank_edits_output, rank_edits_output_vcf, rank_edits_output_bed]
      [sorted_bam_output, rmdup_bam_output, filtered_bam_output, mpileup_output, call_snvs_output, format_variants_output, filter_variants_output, filter_known_snp_output, rank_edits_output, rank_edits_output_bed]
    

