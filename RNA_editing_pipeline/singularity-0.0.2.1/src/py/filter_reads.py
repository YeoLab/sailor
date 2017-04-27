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


def filter_reads(input_bam, output_bam, min_overhang, min_underhang,
                 non_ag_mm_threshold):
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
    for read in i:
        try:
            flag = 1  # start out as a 'good' read
            
            """
            Throw out unmapped reads
            """
            if read.is_unmapped:
                flag = 2
                continue
            try:
                mm = read.get_tag('MD')
            except KeyError:
                mm = ''
            cigar = read.cigarstring
            read_seq = read.query_sequence
            
            """
            Takes care of soft clipped bases
            (remove bases from the read_seq which are soft clipped
            to not interfere with mis-alignments downstream)
            """
            softclip_regex = ur"^(\d+)S"
            softclip = re.findall(softclip_regex,cigar)
            if softclip:
                if len(softclip) == 2:
                    softclip2 = softclip[1]
                    read_seq = read_seq[:-(int(softclip2))]  # remove reads
                softclip1 = softclip[0]
                read_seq = read_seq[int(softclip1):]  # remove reads
                    
            """
            # 5b) Check for small junction overhangs.
            If junction over hang is small, remove read
            """
            cigar_overhang_regex = ur"^(\d+)M.*[\D](\d+)M$"
            
            overhangs = re.findall(cigar_overhang_regex,cigar)
                    
            if overhangs:
                overhangs = overhangs[0]
                if len(overhangs) == 1:
                    if int(overhangs[0]) < min_overhang:
                        flag = 3
                elif len(overhangs) == 2:
                    if (int(overhangs[1]) < min_overhang) or (int(overhangs[0]) < min_overhang):
                        flag = 4
                    
            """
            # 5c) If there exists short indels, remove them.
            """
            if 'I' in cigar or 'D' in cigar:
                # print('filtered out indels (cigar={})'.format(cigar))
                flag = 5
                # print(read)
            
            """
            # 2) If primary not primary alignment, throw out
            """
    
            if read.is_secondary:
                flag = 6
                # print(read)
            """
            # MD:Z tag-based filters
            """
            flank_mm_regex = ur"^(\d+).*[ACGT](\d+)$"
            flank_mm = re.findall(flank_mm_regex,mm)
            if flank_mm:
                flank_mm = flank_mm[0]
                if flank_mm[1]:
                    if int(flank_mm[1]) < min_underhang:
                        flag = 7
                if flank_mm[0]:
                    if int(flank_mm[0]) < min_underhang:
                        flag = 8
            
            """
            # Manually setting reversed reads to 'sense' strand per truseq
            library protocols
            """

            sense = True if read.is_reverse == True else False
            
            """
            # 5c) Search MDZ for A, T's in reference, if mutations are not 
            #     A-G (sense) or T-C (antisense), add to non_ag_mm_counts
            #     threshold. If non_ag_mm_counts > threshold, toss the whole
            #     read. Otherwise, allow up to the maximum allowable non-AG
            #     mismatches before tossing. Default: 1 mm
            """
            mismatches_regex = ur"(\d+)([ATCG])"
            mismatches = re.findall(mismatches_regex,mm)
            if mismatches:
                read_pos = 0
                non_ag_mm_counts = 0
                for mismatch in mismatches:
                    ref_allele = mismatch[1]
                    read_pos += int(mismatch[0])
                                
                    read_allele = read_seq[read_pos]
                        
                    if(not((ref_allele == 'A' and read_allele == 'G' and sense == True) or \
                           (ref_allele == 'T' and read_allele == 'C' and sense == False))):
                        non_ag_mm_counts += 1
                        if non_ag_mm_counts > non_ag_mm_threshold:
                            flag = 9
                            break
                    read_pos += 1

            if flag == 1:
                o.write(read)
        except TypeError as e:
            print("error! {}".format(e))
            print(read)
    i.close()
    o.close()


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
        # Process arguments

        args = parser.parse_args()
        input_bam = args.input_bam
        output_bam = args.output_bam
        min_overhang = args.min_overhang
        min_underhang = args.min_underhang
        non_ag_mm_threshold = args.non_ag_mm_threshold
        
        filter_reads(
            input_bam,
            output_bam,
            min_overhang,
            min_underhang,
            non_ag_mm_threshold
        )
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