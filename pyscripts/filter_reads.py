#!/usr/bin/env python
# encoding: utf-8
'''
editing.filter_reads -- BAM filtering script

filters reads to clean BAM files of sequencing errors at the end of reads and
unexpected non-AG mutations. Also conservatively removes reads with small
junction overhangs and trims any softclipping that may have occurred within
the read.

@author:     brian

@copyright:  2016 yeolab. All rights reserved.

@license:    license

@contact:    bay001@ucsd.edu
@deffield    updated: 4-21-2017
'''

import sys
import os
import re
import pysam
from collections import defaultdict

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2016-07-13'
__updated__ = '2017-04-21'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


def get_softclip(cigar):
    """
    Returns the number of bases to be softclipped on either left or right
    side. Or both. If not softclipped, return 0

    :param cigar: string
        BAM/SAM CIGAR string
    :return left: int
        number of softclipped reads at the beginning
    :return right: int
        number of softclipped reads at the end
    """
    softclip_regex = ur"(\d+)S"
    softclip = re.findall(softclip_regex,cigar)

    softclip_right_regex = ur"[\w\d]{1}(\d+)S" # if the softclip comes from the right side
    softclip_right = re.findall(softclip_right_regex,cigar)

    left = 0
    right = 0

    if softclip:
        if len(softclip) == 2: # softclipped on both sides
            left = int(softclip[0])
            right = int(softclip[1])
        elif len(softclip_right) == 1: # softclipped only on the RIGHT side
            right = int(softclip[0])
        else: # softclipped only on the LEFT side
            left = int(softclip[0])
    return left, right


def remove_softclipped_reads(left, right, read_seq):
    """
    Returns the read after removing softclipped bases.
    :param left: int
        left softclip
    :param right: int
        right softclip
    :param read_seq: string
        read sequence
    :return softclipped_read_sequence: string


    """
    if right == 0:
        return read_seq[left:]
    return read_seq[left:-right]


def get_junction_overhangs(cigar):
    """
    Returns the number of reads left/right of a junction as indicated
    by the N in a cigar string. Return -1, -1 for reads that don't span
    junctions.

    :param cigar: string
    :return left: int
    :return right: int
    """
    cigar_overhang_regex = ur"(\d+)M[\d]+N(\d+)M"

    overhangs = re.findall(cigar_overhang_regex, cigar)
    if overhangs:
        return int(overhangs[0][0]), int(overhangs[0][1])
    else:
        return -1, -1


def is_mismatch_before_n_flank_of_read(md, n):
    """
    Returns True if there is a mismatch before the first n nucleotides
    of a read, or if there is a mismatch before the last n nucleotides
    of a read.

    :param md: string
    :param n: int
    :return is_mismatch: boolean
    """
    is_mismatch = False
    flank_mm_regex = ur"^(\d+).*[ACGT](\d+)$"
    flank_mm = re.findall(flank_mm_regex,md)
    if flank_mm:
        flank_mm = flank_mm[0]
        if flank_mm[1]:
            if int(flank_mm[1]) < n:
                is_mismatch = True
        if flank_mm[0]:
            if int(flank_mm[0]) < n:
                is_mismatch = True
    return is_mismatch


def non_ag_mismatches(read_seq, md, sense):
    """
    Given a read sequence, MD tag, and 'sense' (look for AG if sense,
    look for TC if antisense), return the number of non-AG/TC mismatches
    seen in the read.

    :param read_seq: string
    :param md: string
    :param sense: boolean
    :return nonAG: int
    """
    mismatches_regex = ur"(\d+)([ATCG])"
    mismatches = re.findall(mismatches_regex,md)
    non_ag_mm_counts = 0
    if mismatches:
        read_pos = 0
        for mismatch in mismatches:
            ref_allele = mismatch[1]
            read_pos += int(mismatch[0])

            read_allele = read_seq[read_pos]
            if(not((ref_allele == 'A' and read_allele == 'G' and sense == True) or
                   (ref_allele == 'T' and read_allele == 'C' and sense == False))):
                non_ag_mm_counts += 1
            read_pos += 1

    return non_ag_mm_counts


def filter_reads(
        input_bam, output_bam, min_overhang, min_underhang,
        non_ag_mm_threshold, reverse_stranded=True,
):
    """
    # Step 3: filter reads

    Per Boyko/Mike Washburn's editing paper:

    b) it had a junction overhang < 10nt according to its SAMtools CIGAR string
    c) it had > 1 non-A2G or non-C2T mismatch or any short indel, per its MD tag
    d) it had a mismatch less than 25nt away from either end of the read
    (this was changed to 5nt in the relaxed version used for quantification)

    * Removed 5d per discussions with the Hundley lab.

    :param input_bam: basestring
    :param output_bam: basestring
    :param min_overhang: int
        minimum number required to span a junction (filter b)
    :param min_underhang: int
        minimum number required at the end of the read (filter c)
    :param non_ag_mm_threshold: int
        any more non A-G mismatches than this will filter the read.
    :return:
    """

    print("Filtering reads on: {}".format(input_bam))
    i = pysam.AlignmentFile(input_bam)
    o = pysam.AlignmentFile(output_bam, "wb", template=i)
    flags = defaultdict(list) # number of flags in the bam file
    for read in i:
        try:
            flag = 1  # start out as a 'good' read
            cigar = read.cigarstring
            read_seq = read.query_sequence
            read_name = read.query_name
            """
            Throw out unmapped reads
            """
            if read.is_unmapped:
                flags['unmapped'].append(read.name)
                flag = 2
            try:
                mm = read.get_tag('MD')
            except KeyError:
                mm = ''

            """
            Takes care of soft clipped bases
            (remove bases from the read_seq which are soft clipped
            to not interfere with mis-alignments downstream)
            """
            left_softclip, right_softclip = get_softclip(cigar)
            read_seq = remove_softclipped_reads(left_softclip, right_softclip, read_seq)

            """
            # 5b) Check for small junction overhangs.
            If junction over hang is small, remove read
            """

            left_overhang, right_overhang = get_junction_overhangs(cigar)
            if left_overhang != -1 and right_overhang != -1:
                if left_overhang < min_overhang or right_overhang < min_overhang:
                    flags['small_overhang'].append(read_name)
                    flag = 3
            elif left_overhang != -1:
                print("Warning: CIGAR {} has weird junction mark (or the regex is wrong)")

            """
            # 5c) If there exists indels, remove them.
            """
            if 'I' in cigar or 'D' in cigar:
                flags['indel'].append(read_name)
                flag = 4

            """
            # 2) If primary not primary alignment, throw out
            """
    
            if read.is_secondary:
                flags['not_primary'].append(read_name)
                flag = 5

            """
            # MD:Z tag-based filters. If there is a mismatch on either end of the read, throw out.
            """

            if is_mismatch_before_n_flank_of_read(mm, min_underhang):
                flags['small_underhang'].append(read_name)
                flag = 6

            """
            # Manually setting reversed reads to 'sense' strand per truseq
            library protocols (Default is truseq reverse stranded)
            """
            if reverse_stranded:
                sense = True if read.is_reverse == True else False
            else:
                sense = True if read.is_reverse == False else False

            """
            # 5c) Search MDZ for A, T's in reference, if mutations are not 
            #     A-G (sense) or T-C (antisense), add to non_ag_mm_counts
            #     threshold. If non_ag_mm_counts > threshold, toss the whole
            #     read. Otherwise, allow up to the maximum allowable non-AG
            #     mismatches before tossing. Default: 1 mm
            """
            if non_ag_mismatches(read_seq, mm, sense) > non_ag_mm_threshold:
                flags['non_ag_exceeded'].append(read_name)
                flag = 7

            if flag == 1:
                o.write(read)
        except TypeError as e:
            print("error! {}".format(e))
    i.close()
    o.close()
    return flags


def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date
    )
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2016 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license,
            formatter_class=RawDescriptionHelpFormatter
        )
        parser.add_argument(
            '-V', '--version',
            action='version',
            version=program_version_message
        )
        parser.add_argument(
            "-i", "--input",
            dest="input_bam",
            help="sorted rmdup bam file for filtering",
            required=True
        )
        parser.add_argument(
            "-o", "--output",
            dest="output_bam",
            help="output bam filtered per editing rules",
            required=True
        )
        parser.add_argument(
            "-j", "--junction_overhang",
            dest="min_overhang",
            help="minimum junction overhang needed to start "
                 "counting mutations",
            required=False,
            type=int,
            default=10
        )
        parser.add_argument(
            "-e", "--edge_mutation",
            dest="min_underhang",
            help="minimum nt away from read end to call valid mutation",
            required=False,
            type=int, default=0
        )
        parser.add_argument(
            "-ag", "--non_ag_threshold",
            dest="non_ag_mm_threshold",
            help="allow up to [n] non-AG mutations in a read before tossing."
                 " Default: 1",
            required=False,
            type=int,
            default=1
        )
        parser.add_argument(
            "-s", "--save-filtered",
            dest="save_filtered",
            help="save filtered readsnames",
            required=False,
            action='store_true'
        )
        # Process arguments

        args = parser.parse_args()
        input_bam = args.input_bam
        output_bam = args.output_bam
        min_overhang = args.min_overhang
        min_underhang = args.min_underhang
        non_ag_mm_threshold = args.non_ag_mm_threshold
        save_filtered = args.save_filtered

        flags = filter_reads(
            input_bam,
            output_bam,
            min_overhang,
            min_underhang,
            non_ag_mm_threshold
        )
        if save_filtered:
            print('saving filtered readnames to file...')
            for flag, lst in flags.iteritems():
                o = open(output_bam + '.{}'.format(flag), 'w')
                o.write('\n'.join(lst))
                o.close()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'editing.filter_reads_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())