#!/usr/env python

import os
import pytest
from pyscripts import filter_reads as fr

### TEST SOFTCLIP ###

def test_left_softclipped_1():
    cigar = '1S51M47N90M'
    left, right = fr.get_softclip(cigar)
    assert left == 1
    assert right == 0

def test_right_softclipped_1():
    cigar = '73M740N29M1S'
    left, right = fr.get_softclip(cigar)
    assert left == 0
    assert right == 1

def test_both_softclipped_1():
    cigar = '40S51M47N63M1S'
    left, right = fr.get_softclip(cigar)
    assert left == 40
    assert right == 1

def test_none_softclipped_1():
    cigar = '55M'
    left, right = fr.get_softclip(cigar)
    assert left == 0
    assert right == 0

### TEST SOFTCLIP REMOVAL ###

def test_left_remove_softclip():
    read = 'TTTCGTCGTCAGAATTCGCGGTATCAACCAGCTTCATCCAAAGCCAAGAAAGGCTCTCCAGATCCTCCGTCTTCGTCAGATCAACAACGGAGTGTTCGTCAAGCTGAACAAGGCTACTCTTCCACTTCTCCGTATCATCGAG'
    cigar = '1S51M47N90M'
    left, right = fr.get_softclip(cigar)
    new_read = fr.remove_softclipped_reads(left, right, read)
    assert new_read == 'TTCGTCGTCAGAATTCGCGGTATCAACCAGCTTCATCCAAAGCCAAGAAAGGCTCTCCAGATCCTCCGTCTTCGTCAGATCAACAACGGAGTGTTCGTCAAGCTGAACAAGGCTACTCTTCCACTTCTCCGTATCATCGAG'
    assert len(new_read) == len(read) - left - right

def test_right_remove_softclip():
    read = 'CGTCGAATAACCGTTTCTCGTGATTTGTCACATTATCCTTGAGCACAATACATCCACCAGGTTTCAGTCCTTTCGCACATCTTTTAAAGAAATCAACCAAATA'
    cigar = '73M740N29M1S'
    left, right = fr.get_softclip(cigar)
    new_read = fr.remove_softclipped_reads(left, right, read)

    assert new_read == 'CGTCGAATAACCGTTTCTCGTGATTTGTCACATTATCCTTGAGCACAATACATCCACCAGGTTTCAGTCCTTTCGCACATCTTTTAAAGAAATCAACCAAAT'
    assert len(new_read) == len(read) - left - right

def test_both_remove_softclip():
    read = 'TACATCGGTGACTGGAGTTCAGACGTGGCTCTTCCGATCTTTCGTCGTCAGAATTCGCGGTATCAACCAGCTTCATCCAAAGCCAAGAAAGGCTCTCCAGATCCTCCGTCTTCGTCAGATCAACAACGGAGTGTTCGTCAAGCTGAACAAGGCTC'
    cigar = '40S51M47N63M1S'
    left, right = fr.get_softclip(cigar)
    new_read = fr.remove_softclipped_reads(left, right, read)

    assert new_read == 'TTCGTCGTCAGAATTCGCGGTATCAACCAGCTTCATCCAAAGCCAAGAAAGGCTCTCCAGATCCTCCGTCTTCGTCAGATCAACAACGGAGTGTTCGTCAAGCTGAACAAGGCT'
    assert len(new_read) == len(read) - left - right

### TEST JUNCTION OVERHANG ###

def test_junction_overhang_1():
    """
    test large junction overhangs on each side
    :return:
    """
    cigar = '1S51M47N90M'
    min_overhang = 10
    left, right = fr.get_junction_overhangs(cigar, min_overhang)
    assert left == 51 and right == 90

def test_junction_overhang_2():
    """
    Test no junction overhangs
    :return:
    """
    cigar = '255M'
    min_overhang = 10
    left, right = fr.get_junction_overhangs(cigar, min_overhang)
    assert left == -1 and right == -1

def test_junction_overhang_3():
    """
    Test multiple junction overhangs with softclipped read
    :return:
    """
    cigar = '1S53M56N72M3261N8M'
    min_overhang = 10
    left, right = fr.get_junction_overhangs(cigar, min_overhang)
    assert left == 53 and right == 8

def test_junction_overhang_4():
    """
    Test multiple junction overhangs with softclipped read and indel
    :return:
    """
    cigar = '1S53M56N72M3261N8M1I100M'
    min_overhang = 10
    left, right = fr.get_junction_overhangs(cigar, min_overhang)
    assert left == 53 and right == 8

def test_junction_overhang_5():
    """
    Test junction overhang with hardclipped reads
    :return:
    """
    cigar = '66H35M100N100M'
    min_overhang = 10
    left, right = fr.get_junction_overhangs(cigar, min_overhang)
    assert left == 35 and right == 100

### TEST UNDERHANG MISMATCHES ###

def test_is_mismatch_before_n_flank_of_read_1():
    # mismatch in the middle
    md = '63A68'
    n = 5
    assert fr.is_mismatch_before_n_flank_of_read(md, n) == False

def test_is_mismatch_before_n_flank_of_read_2():
    # test behavior on insert
    md = '37IGC70G12'
    n = 5
    assert fr.is_mismatch_before_n_flank_of_read(md, n) == False

def test_is_mismatch_before_n_flank_of_read_3():
    # test behavior on del
    md = '37^GC70G12'
    n = 5
    assert fr.is_mismatch_before_n_flank_of_read(md, n) == False

def test_is_mismatch_before_n_flank_of_read_4():
    # mismatch at 4th from the right
    md = '151C4'
    n = 5
    assert fr.is_mismatch_before_n_flank_of_read(md, n) == True

def test_is_mismatch_before_n_flank_of_read_5():
    # no mismatches
    md = '155'
    n = 5
    assert fr.is_mismatch_before_n_flank_of_read(md, n) == False

def test_is_mismatch_before_n_flank_of_read_6():
    # mismatch 4 from the left
    md = '4A0G112'
    n = 5
    assert fr.is_mismatch_before_n_flank_of_read(md, n) == True

### TEST NON AG MISMATCHES ###

def test_non_ag_mismatches_1():
    # No mismatches
    read_seq = 'ACGCCTCGGAGTCAACCCGGAGGAAGTTTTGGCGGATCTTCGTGCTCGTAATCAATTCCAATAAATATTCTTTGCCCTAAATACTTTAAATTATCCATCTGACAACTAAAATTTCGGTTCTTCTTGGCTTCTTCTATTTGTGAAATGGTTTATTT'
    md = '155'
    sense = True
    assert fr.non_ag_mismatches(read_seq, md, sense) == 0

def test_non_ag_mismatches_2():
    # One non-ag mismatch
    read_seq = 'CCAAAATTCAGCCCGCGAAGGCATGACGTCAGCGCAAGGCAGTAGTTTCCAGAAGAACTCTGTCGTCTACCTTAATGCCTCAAATGCGAACCCGCTTCGGCCATCCTTCTCGCTCAGAGAATGGATTAGAGTTCTA'
    md = '35G99'
    sense = False
    assert fr.non_ag_mismatches(read_seq, md, sense) == 1

def test_non_ag_mismatches_3():
    # One AG mismatch
    read_seq = 'ATCG'
    md = '2T1'
    sense = False
    assert fr.non_ag_mismatches(read_seq, md, sense) == 0

def test_non_ag_mismatches_4():
    # One TC(-) mismatch, one non-ag mismatch (TA)
    read_seq = 'ATCGA'
    md = '2T1T'
    sense = False
    assert fr.non_ag_mismatches(read_seq, md, sense) == 1

def test_non_ag_mismatches_5():
    # One AG(+) mismatch, two non-ag mismatch (TC, TC)
    read_seq = 'CCCCCCCCCCGCCCCC'
    md = '10A3T0T10'
    sense = True
    assert fr.non_ag_mismatches(read_seq, md, sense) == 2