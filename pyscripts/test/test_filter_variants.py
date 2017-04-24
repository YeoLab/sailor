#!/usr/env python

import os
import pytest
from pyscripts import filter_variants as fv

def test_dp_coverage():
    min_coverage = 1
    attr_string = 'DP=7;DP4=6,0,1,0;'

    fv.pass_min_coverage()