#!/usr/env python

import os
import pytest
from pyscripts import filter_variants as fv

### TEST GET COVERAGE DATA FROM VCF FILE ###

def test_get_dp_and_i_1():
    # using simple info attribute
    info = 'DP=7;DP4=6,0,1,0;'

    dp, dp4 = fv.get_dp_and_i(info)
    assert dp == '7'
    assert dp4 == '6,0,1,0'

def test_get_dp_and_i_2():
    # using a real line from VCF
    info = 'DP=1;DPR=1;MQ0F=0;AF1=0;AC1=0;DP4=1,0,0,0;MQ=20;FQ=-37.569'
    dp, dp4 = fv.get_dp_and_i(info)
    assert dp == '1'
    assert dp4 == '1,0,0,0'

### TEST SPLIT I AND ALLELES ###

def test_split_i_and_get_allele_1():
    """
    Reverse_stranded library
    i[0] = forward ref allele
    i[1] = reverse ref allele
    i[2] = forward non-ref allele
    i[3] = reverse non-ref allele
    :return:
    """
    i = '0,3,0,3'
    ref, alt, sense = fv.split_i_and_get_allele(i, reverse_split=True)
    assert sense == False
    assert ref == 3
    assert alt == 3


def test_split_i_and_get_allele_2():
    """
    Forward stranded library
    i[0] = forward ref allele
    i[1] = reverse ref allele
    i[2] = forward non-ref allele
    i[3] = reverse non-ref allele
    :return:
    """
    i = '0,3,0,3'
    ref, alt, sense = fv.split_i_and_get_allele(i, reverse_split=False)
    assert sense == True
    assert ref == 3
    assert alt == 3


def test_split_i_and_get_allele_3():
    """
    Reverse_stranded library TIE
    i[0] = forward ref allele
    i[1] = reverse ref allele
    i[2] = forward non-ref allele
    i[3] = reverse non-ref allele
    :return:
    """
    i = '3,3,3,3'
    ref, alt, sense = fv.split_i_and_get_allele(i, reverse_split=True)
    assert sense == False
    assert ref == 6
    assert alt == 6

def test_split_i_and_get_allele_4():
    """
    Reverse_stranded library TIE
    i[0] = forward ref allele
    i[1] = reverse ref allele
    i[2] = forward non-ref allele
    i[3] = reverse non-ref allele
    :return:
    """
    i = '29,26,0,24'
    ref, alt, sense = fv.split_i_and_get_allele(i, reverse_split=True)
    assert sense == False
    assert ref == 26+29
    assert alt == 24

def test_split_i_and_get_allele_5():
    """
    Forward stranded library TIE
    i[0] = forward ref allele
    i[1] = reverse ref allele
    i[2] = forward non-ref allele
    i[3] = reverse non-ref allele
    :return:
    """
    i = '3,3,3,3'
    ref, alt, sense = fv.split_i_and_get_allele(i, reverse_split=False)
    assert sense == True
    assert ref == 6
    assert alt == 6

### TEST PASS EDITING SITE PHENOTYPE ###

def test_pass_editing_site_phenotype_1():
    # sense strand editing
    ref = 'A'
    alt = 'G'
    sense = True
    assert fv.pass_editing_site_phenotype(ref, alt, sense) == True

def test_pass_editing_site_phenotype_2():
    ref = 'T'
    alt = 'C'
    sense = False
    assert fv.pass_editing_site_phenotype(ref, alt, sense) == True

def test_pass_editing_site_phenotype_3():
    ref = 'A'
    alt = 'G'
    sense = False
    assert fv.pass_editing_site_phenotype(ref, alt, sense) == False

def test_pass_editing_site_phenotype_4():
    ref = 'T'
    alt = 'C'
    sense = True
    assert fv.pass_editing_site_phenotype(ref, alt, sense) == False

def test_pass_fail_variant_1():
    """
    Tests the DP4 flag filter
    :return:
    """
    vcf_file = 'test/vcf/pass_fail_variant_1.vcf'
    output_eff = 'test/vcf/pass_fail_variant_1.eff'
    min_coverage = 5
    cov_metric = 'DP4'
    reverse_split = False

    flags = fv.vcf2eff(vcf_file, output_eff, min_coverage, cov_metric, reverse_split)
    assert flags['min_coverage'] == ['chrI:4295']

def test_pass_fail_variant_2():
    """
    Tests the DP flag filter
    :return:
    """
    vcf_file = 'test/vcf/pass_fail_variant_2.vcf'
    output_eff = 'test/vcf/pass_fail_variant_2.eff'
    min_coverage = 5
    cov_metric = 'DP'
    reverse_split = False

    flags = fv.vcf2eff(vcf_file, output_eff, min_coverage, cov_metric, reverse_split)
    assert flags['min_coverage'] == ['chrI:4295']


### These are all mostly trivial, we don't guess the strand of the gene
#   that we map to anymore. Now we are explicit since we split the bam files
#   before hand (5-4-17).


def test_pass_fail_variant_3():
    """
    passes if we see an A/G variant on the forward strand,
    when the library is forward stranded
    :return:
    """
    vcf_file = 'test/vcf/pass_fail_variant_3.vcf'
    output_eff = 'test/vcf/pass_fail_variant_3.eff'
    min_coverage = 5
    cov_metric = 'DP'
    reverse_split = False

    flags = fv.vcf2eff(vcf_file, output_eff, min_coverage, cov_metric, reverse_split)
    assert flags['not_editing'] == ['chrI:4295']

def test_pass_fail_variant_4():
    """
    passes if we see a T/C variant on the forward strand,
    when the library is reverse stranded
    :return:
    """
    vcf_file = 'test/vcf/pass_fail_variant_4.vcf'
    output_eff = 'test/vcf/pass_fail_variant_4.eff'
    min_coverage = 5
    cov_metric = 'DP'
    reverse_split = True

    flags = fv.vcf2eff(vcf_file, output_eff, min_coverage, cov_metric, reverse_split)
    assert flags['not_editing'] == ['chrI:3771']

def test_pass_fail_variant_5():
    """
    passes if we see a T/C variant on the reverse strand,
    when the library is forward stranded.
    :return:
    """
    vcf_file = 'test/vcf/pass_fail_variant_5.vcf'
    output_eff = 'test/vcf/pass_fail_variant_5.eff'
    min_coverage = 5
    cov_metric = 'DP'
    reverse_split = True

    flags = fv.vcf2eff(vcf_file, output_eff, min_coverage, cov_metric, reverse_split)
    assert flags['not_editing'] == ['chrI:3771']

def test_pass_fail_variant_6():
    """
    passes if we see an A/G variant on the reverse strand,
    when the library is reverse stranded
    :return:
    """
    vcf_file = 'test/vcf/pass_fail_variant_6.vcf'
    output_eff = 'test/vcf/pass_fail_variant_6.eff'
    min_coverage = 5
    cov_metric = 'DP'
    reverse_split = True

    flags = fv.vcf2eff(vcf_file, output_eff, min_coverage, cov_metric, reverse_split)
    assert flags['not_editing'] == ['chrI:3771']

