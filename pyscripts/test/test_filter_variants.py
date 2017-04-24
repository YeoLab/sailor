#!/usr/env python

import os
import pytest
from pyscripts import filter_variants as fv

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

