#!/usr/env python

import os
import pytest
from pyscripts import rank_edits as r

### TEST 100% EDITED FILTER ###

def test_process_1():
    """
    tests the 100% edited filter
    :return:
    """
    alfa = 0
    beta = 0
    cov_margin = 0.01
    with open('vcf/rank_edit_variant_1.eff', 'r') as f:
        line = f.readline()
        output_string = r.process(alfa, beta, cov_margin, True, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'PASS'

        output_string = r.process(alfa, beta, cov_margin, False, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'POSSIBLE_SNP'

def test_process_2():
    """
    tests the 100% edited filter
    :return:
    """
    alfa = 1
    beta = 0
    cov_margin = 0.01
    with open('vcf/rank_edit_variant_1.eff', 'r') as f:
        line = f.readline()
        output_string = r.process(alfa, beta, cov_margin, True, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'PASS'

        output_string = r.process(alfa, beta, cov_margin, False, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'POSSIBLE_SNP'


def test_process_2():
    """
    tests the 100% edited filter
    :return:
    """
    alfa = 1
    beta = 0
    cov_margin = 0.01
    with open('vcf/rank_edit_variant_1.eff', 'r') as f:
        line = f.readline()
        output_string = r.process(alfa, beta, cov_margin, True, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'PASS'

        output_string = r.process(alfa, beta, cov_margin, False, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'POSSIBLE_SNP'


def test_process_3():
    """
    tests the standard conf score
    :return:
    """
    from scipy.special import betainc

    a = 0
    b = 0
    cov_margin = 0.01
    total_coverage = 100
    dp4 = '50,0,50,0'
    fraction = 0.5
    # confidence = 1 - betainc(G, A, cov_margin)
    keep_all_edited = False
    test_vcf_line = 'chrI	15542	{}	A	G	{}	.	DP={};DPR=4,1;SGB=-0.379885;RPB=1;MQB=1;BQB=1;MQ0F=0;AF1=0.406103;AC1=1;DP4={};MQ=20;FQ=-29.53;PV4=1,1,1,1	GT:PL:DP:DV:SP:DP4:DPR	0/0:5,0,47:5:1:0:0,4,0,1:4,1'.format(
        total_coverage,
        fraction,
        total_coverage,
        dp4
    )
    result_line = r.process(a, b, cov_margin, keep_all_edited, test_vcf_line)
    result_line = result_line.split('\t')
    assert result_line[5] == '1.0'

def test_process_4():
    """
    tests the standard conf score (a = G, b = A)
    :return:
    """
    from scipy.special import betainc

    a = 0 # pseudocount
    b = 0 # pseudocount
    cov_margin = 0.01
    total_coverage = 5
    dp4 = '4,0,1,0'
    fraction = 0.2
    # confidence = 1 - betainc(G, A, cov_margin)
    keep_all_edited = False
    test_vcf_line = 'chrI	15542	{}	A	G	{}	.	DP={};DPR=4,1;SGB=-0.379885;RPB=1;MQB=1;BQB=1;MQ0F=0;AF1=0.406103;AC1=1;DP4={};MQ=20;FQ=-29.53;PV4=1,1,1,1	GT:PL:DP:DV:SP:DP4:DPR	0/0:5,0,47:5:1:0:0,4,0,1:4,1'.format(
        total_coverage,
        fraction,
        total_coverage,
        dp4
    )
    result_line = r.process(a, b, cov_margin, keep_all_edited, test_vcf_line)
    result_line = result_line.split('\t')
    assert result_line[5] == '0.96059601'

def test_process_4():
    """
    tests the standard conf score (a = G, b = A)
    :return:
    """
    from scipy.special import betainc

    a = 0 # pseudocount
    b = 0 # pseudocount
    cov_margin = 0.01
    total_coverage = 5
    dp4 = '3,0,2,0'
    fraction = 0.4
    # confidence = 1 - betainc(G, A, cov_margin)
    keep_all_edited = False
    test_vcf_line = 'chrI	15542	{}	A	G	{}	.	DP={};DPR=4,1;SGB=-0.379885;RPB=1;MQB=1;BQB=1;MQ0F=0;AF1=0.406103;AC1=1;DP4={};MQ=20;FQ=-29.53;PV4=1,1,1,1	GT:PL:DP:DV:SP:DP4:DPR	0/0:5,0,47:5:1:0:0,4,0,1:4,1'.format(
        total_coverage,
        fraction,
        total_coverage,
        dp4
    )
    result_line = r.process(a, b, cov_margin, keep_all_edited, test_vcf_line)
    result_line = result_line.split('\t')
    assert result_line[5] == '0.99940797'

def test_process_5():
    """
    makes sure the conf score doesn't get changed
    :return:
    """
    from scipy.special import betainc

    a = 0 # pseudocount
    b = 0 # pseudocount
    cov_margin = 0.01
    total_coverage = 100
    dp4 = '99,0,1,0'
    fraction = 0.01
    # confidence = 1 - betainc(G, A, cov_margin)
    keep_all_edited = False
    test_vcf_line = 'chrI	15542	{}	A	G	{}	.	DP={};DPR=4,1;SGB=-0.379885;RPB=1;MQB=1;BQB=1;MQ0F=0;AF1=0.406103;AC1=1;DP4={};MQ=20;FQ=-29.53;PV4=1,1,1,1	GT:PL:DP:DV:SP:DP4:DPR	0/0:5,0,47:5:1:0:0,4,0,1:4,1'.format(
        total_coverage,
        fraction,
        total_coverage,
        dp4
    )
    result_line = r.process(a, b, cov_margin, keep_all_edited, test_vcf_line)
    result_line = result_line.split('\t')
    assert result_line[5] == '0.369729638'
