#!/usr/bin/env python
# encoding: utf-8
'''
editing.filter_variants -- vcf filtering script

filters generic variants from TruSeq RNA-SEQ sourced vcf files

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


def pass_min_coverage(dp, i, min_coverage, cov_metric):
    """
    if the DP flag does not meet minimum coverage, toss it.
    if the DP4 flag does not meet minimum coverage, toss it.
    :param dp:
        DP coverage allele depth
    :param i: string
        DP4 coverage allele depth
    :param min_coverage: int
        minimum coverage required (anything less will return False)
    :param cov_metric: string
        either 'DP' or 'DP4'
    :return passed: boolean
        True if the coverage is at least min_coverage, false otherwise.
    """
    i = i.split(',')
    if (cov_metric == 'DP') and (int(dp) < min_coverage):
        return False
    elif (cov_metric == 'DP4') and ((int(i[0]) + int(i[2]) + int(
            i[1]) + int(i[3])) < min_coverage):
        return False

    return True


def pass_editing_site_phenotype(ref, alt, sense, ct, gt):
    """
    Returns True if it looks like an editing site (A-G or T-C antisense).

    :param ref: string
    :param alt: string
    :param sense: boolean
    :param ct: boolean
    :return passed: boolean
        True if it looks like an editing site
    """

    # handle multiallelic callers if necessary (not perfect)
    if ct:
        if ((ref == 'C' and alt.find('T') == -1) or
            (ref == 'G' and alt.find('A') == -1)):
            return False
    elif gt:
        if ((ref == 'G' and alt.find('T') == -1) or
            (ref == 'C' and alt.find('A') == -1)):
    else:
        if ((ref == 'A' and alt.find('G') == -1) or
            (ref == 'T' and alt.find('C') == -1)):
            return False
    # sense variants must have A as ref, antisense must have T
    if ct:
        if (sense and ref != 'C') or (not sense and ref != 'G'):
            return False
    elif gt:
        if (sense and ref != 'G') or (not sense and ref != 'C'):
            return False
    else:
        if (sense and ref != 'A') or (not sense and ref != 'T'):
            return False
    return True


def get_dp_and_i(info):
    """
    Returns the dp and dp4 coverage attributes.
    :param info: string
        the info (attribute) string in a vcf file.
    :return dp: string
        coverage defined by DP
    :return dp4: string
        comma separated coverage defined by DP4
    """
    regex = 'DP\=(\d+)\;.*DP4\=([\d\,]+)'
    dp, i = re.findall(regex, info)[0]
    return dp, i


def split_i_and_get_allele(i, reverse_split, unstranded=False):
    """
    Splits i and returns the ref and alt numbers.

    i[0] = forward ref allele
    i[1] = reverse ref allele
    i[2] = forward non-ref allele
    i[3] = reverse non-ref allele

    logic: if there are more ref/non-ref alleles on the
    forward strand, the SNV must come from the positive reads.
    Vice versa, if there are more ref/non-ref alleles on
    the reverse, SNV must be reverse as well. Strand info is not
    kept in VCF files, so this must be inferred.

    :param i: string
        dp4 string
    :param reverse_split: boolean
        is reversely split in step 1 of the workflow (split_strands.py)
    :return ref_num: int
        number of reads supporting reference allele
    :return alt_num: int
        number of reads supporting alt allele
    :return sense: boolean
        True if the vcf file comes from the 'forward'-designated bam files
    :see

    """
    i = i.split(',')
    fwd_alleles = int(i[0]) + int(i[2])
    rev_alleles = int(i[1]) + int(i[3])
    ref_num = int(i[0]) + int(i[1])
    alt_num = int(i[2]) + int(i[3])
    if reverse_split:
        sense = False
    else:
        sense = True
    # TODO: remove this. May be useful for checking unstranded reads in the future.
    '''
    if reverse_stranded:
        if fwd_alleles <= rev_alleles:
            sense = True
            ref_num = int(i[1])
            alt_num = int(i[3])
        else:
            sense = False
            ref_num = int(i[0])
            alt_num = int(i[2])
    else:
        if fwd_alleles >= rev_alleles:
            sense = True
            ref_num = int(i[0])
            alt_num = int(i[2])
        else:
            sense = False
            ref_num = int(i[1])
            alt_num = int(i[3])
    '''
    return ref_num, alt_num, sense


def vcf2eff(input_vcf, output_eff, min_coverage, cov_metric='DP4',
            reverse_stranded=True, ct=False, gt=False, unstranded=False):
    """
    Step 6: Filter variants for coverage and editing-specific AG/TC changes.

    Converts vcf file into an "eff" file (essentially filtering for
    variants at this step).

    :param input_vcf: basestring
        vcf-formatted file
    :param output_eff: basestring
        vcf-formatted file
    :param min_coverage: int
        minimum coverage required to call a variant
    :param cov_metric: basestring
        the imported vcf file must contain either DP or DP4 flag in the
        attributes area, as this function uses them to define coverage
        over the variant.
    :return:
    """

    print("Calling vcf2eff: {}".format(input_vcf))
    o = open(output_eff, 'w')
    flags = defaultdict(list)
    with open(input_vcf) as f:
        # for line in f:
        for line in f:
            flag = 1  # flag = 1 -> variant good to keep, otherwise toss

            if line.startswith('#'):  # is vcf header
                o.write(line)
            else:
                try:
                    line = line.split('\t')
                    chrom = line[0]
                    pos = line[1]
                    ref = line[3]
                    alt = line[4]

                    dp, i = get_dp_and_i(line[7])


                    """
                    if the DP flag does not meet minimum coverage, toss it.
                    if the DP4 flag does not meet minimum coverage, toss it.
                    """
                    if not pass_min_coverage(dp, i, min_coverage, cov_metric):
                        flag = 2
                        flags['min_coverage'].append('{}:{}'.format(chrom, pos))

                    """
                    Get sense/antisense edits
                    """
                    ref_num, alt_num, sense = split_i_and_get_allele(
                        i, reverse_stranded
                    )

                    """
                    Get edit percentage
                    """
                    if (alt_num + ref_num) > 0:
                        line[5] = str(alt_num / float(alt_num + ref_num))
                    line[2] = str(alt_num + ref_num)

                    """
                    # 6) if not A-G or T-C, then pass

                    """
                    if not pass_editing_site_phenotype(ref, alt, sense, ct, gt):
                        flag = 3
                        flags['not_editing'].append('{}:{}'.format(chrom, pos))
                    """
                    if vcf line survives all filters, write it.
                    """
                    if flag == 1:
                        newline = "\t".join([l for l in line])
                        o.write(newline)
                except IndexError:
                    print(line)
    o.close()
    return flags


def main(argv=None):  # IGNORE:C0111
    """

    :param argv:
    :return:
    """

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
            dest="input_vcf",
            help="variant vcf file for filtering",
            required=True
        )
        parser.add_argument(
            "-o", "--output",
            dest="output_eff",
            help="output vcf (eff) filtered per editing rules",
            required=True
        )
        parser.add_argument(
            "-m", "--min_coverage",
            dest="min_coverage",
            help="minimum allowable read coverage to pass variant filter",
            required=False,
            type=int,
            default=5
        )
        parser.add_argument(
            "-d", "--dp",
            dest="dp",
            help="Use either the DP flag or [DP4] flag when calculating "
                 "coverage (see vcf format for more info)",
            required=False,
            default='DP4'
        )
        parser.add_argument(
            "-s", "--save-filtered",
            dest="save_filtered",
            help="save filtered read names",
            required=False,
            action='store_true'
        )
        parser.add_argument(
            "--reverse-split",
            dest="reverse_split",
            help="vcf originated from reversely flagged reads",
            action='store_true',
            required=False,
            default=False
        )
        parser.add_argument(
            "--unstranded",
            dest="unstranded",
            help="if the library is unstranded, infer strand position based on number of reads on each strand. Overrides --reverse-split",
            action='store_true',
            required=False,
            default=False
        )
        parser.add_argument(
            "--ct",
            dest="ct",
            help="Look for c/t edits instead of a/g",
            action='store_true',
            required=False,
            default=False
        )
        parser.add_argument(
            "--gt",
            dest="gt",
            help="Look for g/t edits instead of a/g",
            action='store_true',
            required=False,
            default=False
        )
        # Process arguments
        args = parser.parse_args()
        input_vcf = args.input_vcf
        output_eff = args.output_eff
        save_filtered = args.save_filtered
        dp = args.dp
        ct = args.ct
        gt = args.gt
        is_reverse = args.reverse_split
        unstranded = args.unstranded
        min_coverage = args.min_coverage

        flags = vcf2eff(input_vcf, output_eff, min_coverage, dp, is_reverse, ct, gt, unstranded)
        if save_filtered:
            print('saving filtered vars to file...')
            for flag, lst in flags.iteritems():
                o = open(output_eff + '.{}'.format(flag), 'w')
                o.write('\n'.join(lst))
                o.close()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise e
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
