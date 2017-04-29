#!/usr/env python

import os
import pytest
import pysam
from pyscripts import split_strands as ss

def test_split_strands_pe_1():
    test_bam = 'test/bam/pe_unsplit_1.bam'
    test_fwd = 'test/bam/pe_split_1_fwd.bam'
    test_rev = 'test/bam/pe_split_1_rev.bam'
    reverse = True
    ss.split_strands(test_bam,test_fwd,test_rev, reverse)
    fwd_handle = pysam.AlignmentFile(test_fwd)
    rev_handle = pysam.AlignmentFile(test_rev)
    for read in rev_handle:
        assert ((read.is_reverse == False and read.is_read1) or
                (read.is_reverse == True and read.is_read2))
    for read in fwd_handle:
        assert ((read.is_reverse == True and read.is_read1) or
                (read.is_reverse == False and read.is_read2))
    fwd_handle.close()
    rev_handle.close()

def test_split_strands_pe_2():
    # TODO: make test for PE forward strand
    pass

def test_split_strands_se_1():
    test_bam = 'test/bam/se_unsplit_1.bam'
    test_fwd = 'test/bam/se_split_1_fwd.bam'
    test_rev = 'test/bam/se_split_1_rev.bam'
    reverse = True
    ss.split_strands(test_bam,test_fwd,test_rev, reverse)
    fwd_handle = pysam.AlignmentFile(test_fwd)
    rev_handle = pysam.AlignmentFile(test_rev)
    for read in fwd_handle:
        assert (read.is_reverse == True)
    for read in rev_handle:
        assert (read.is_reverse == False)
    fwd_handle.close()
    rev_handle.close()

def test_split_strands_se_2():
    test_bam = 'test/bam/se_unsplit_2.bam'
    test_fwd = 'test/bam/se_split_2_fwd.bam'
    test_rev = 'test/bam/se_split_2_rev.bam'
    reverse = False
    ss.split_strands(test_bam,test_fwd,test_rev, reverse)
    fwd_handle = pysam.AlignmentFile(test_fwd)
    rev_handle = pysam.AlignmentFile(test_rev)
    for read in fwd_handle:
        assert (read.is_reverse == False)
    for read in rev_handle:
        assert (read.is_reverse == True)
    fwd_handle.close()
    rev_handle.close()