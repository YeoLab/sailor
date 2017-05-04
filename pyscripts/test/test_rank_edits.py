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
    with open('test/vcf/rank_edit_variant_1.eff', 'r') as f:
        line = f.readline()
        output_string = r.process(alfa, beta, cov_margin, True, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'PASS'

        output_string = r.process(alfa, beta, cov_margin, False, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'SNP'

def test_process_2():
    """
    tests the 100% edited filter
    :return:
    """
    alfa = 1
    beta = 0
    cov_margin = 0.01
    with open('test/vcf/rank_edit_variant_1.eff', 'r') as f:
        line = f.readline()
        output_string = r.process(alfa, beta, cov_margin, True, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'PASS'

        output_string = r.process(alfa, beta, cov_margin, False, line)
        output_string = output_string.split('\t')
        assert output_string[8] == 'SNP'

