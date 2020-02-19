#!/usr/bin/env python
# encoding: utf-8
'''
editing.rank_edits -- BAM filtering script

Given a VCF file, rank potential editing candidates given percentage of
editing and coverage supporting the site.

@author:     boyko

@copyright:  2016 yeolab. All rights reserved.

@license:    license

@contact:    bay001@ucsd.edu
@deffield    updated: 4-21-2017
'''

import sys
import os
import re
from scipy.special import betainc

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2016-07-13'
__updated__ = '2016-07-13'


class CLIError(Exception):
    """
    Generic exception to raise and log different fatal errors.
    """

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def as_bed(line, ct, gt):
    """
    Returns the BED6-formatted line representation of the CONF file.
    :param line:
    :return:
    """
    line = line.split('\t')
    if ct:
        if line[3] == 'G' and line[4] == 'A':
            strand = '-'
        elif line[3] == 'C' and line[4] == 'T':
            strand = '+'
        else:
            print('WARNING: multiallelic SNV found')
            if line[3] == 'C':
                strand = '+'
            elif line[3] == 'G':
                strand = '-'
            else:
                strand = '0'
    elif gt:
        if line[3] == 'C' and line[4] == 'A':
            strand = '-'
        elif line[3] == 'G' and line[4] == 'T':
            strand = '+'
        else:
            print('WARNING: multiallelic SNV found')
            if line[3] == 'G':
                strand = '+'
            elif line[3] == 'C':
                strand = '-'
            else:
                strand = '0'
    else:
        if line[3] == 'T' and line[4] == 'C':
            strand = '-'
        elif line[3] == 'A' and line[4] == 'G':
            strand = '+'
        else:
            print('WARNING: multiallelic SNV found')
            if line[3] == 'A':
                strand = '+'
            elif line[3] == 'T':
                strand = '-'
            else:
                strand = '0'
    bed_name = '{}|{}>{}|{}'.format(
        line[2], line[3], line[4], line[6]
    )
    return '{}\t{}\t{}\t{}\t{}\t{}\n'.format(
        line[0], int(line[1])-1, int(line[1]), bed_name, line[5], strand
    )


def as_vcf(line):
    """
    Returns a VCF-formatted line representation of the CONF file
    :param line:
    :return:
    """
    line = line.split('\t')
    var_identifier = 'cov_{}|editID_{}:{}'.format(line[2], line[0], line[1])
    return '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
        line[0], line[1], var_identifier, line[3], line[4], line[5],
        line[8], line[9], line[10], line[11]
    )


def process(alfa, beta, cov_margin, keep_all_edited, line):
    """
    Calculates, for a single line in a VCF formatted file, the
    confidence score based on depth of coverage and edit fraction %.

    :param line: string
        single vcf formatted line.
    :return confidence: float
        confidence value of the line
    :return return_string: basestring
        full vcf formatted line with confidence
    """
    (chr, pos, dot, ref, alt, qual,
     filter, info, format, cond) = line.split("\t")[:10]

    if chr[0] == "#":
        print line,
        return

    # retrieve total number of reads mapping to position
    infos = info.split(";")
    (dp, i16) = infos[:2]

    assert dp[:2] == "DP"
    num_reads = int(dp[3:])

    """
    # retrieve numbers of A's and G's on forward and reverse strand
    assert i16[:3] == "I16", i16
    (a_fwd, a_rev, g_fwd, g_rev) = (int(x) for x in i16[4:].split(",")[:4])
    print("warning: i16 not available")
    """

    dp4 = re.findall("DP4\=([\d\,]+)", info)[0]

    (a_fwd, a_rev, g_fwd, g_rev) = (int(x) for x in dp4.split(","))

    a = a_fwd + a_rev
    g = g_fwd + g_rev
    num_reads = a + g
    edit_frac = g / float(num_reads)

    # calc smoothed counts and confidence
    G = g + alfa
    A = a + beta
    theta = G / float(G + A)

    ########  MOST IMPORTANT LINE  ########
    # calculates the confidence of theta as
    # P( theta < cov_margin | A, G) ~ Beta_theta(G, A)
    confidence = 1 - betainc(G, A, cov_margin)

    # keep 100% edited sites or toss
    if A == 0 and not keep_all_edited:
        confidence = 0
        region = 'POSSIBLE_SNP'
    else:
        region = 'PASS'

    # print line in CONF format

    return_string = ("\t".join([chr, pos, str(num_reads), ref, alt, ""]) +
                     "\t".join(str(round(y, 9)) for y in [
                         confidence, theta, edit_frac
                     ]) +
                     "\t".join(["", region, info, format, cond]) +
                     "\n")
    return return_string


def rank_edits(alfa, beta, cov_margin, keep_all_edited, eff_file, outfile, ct=False, gt=False):
    """
    Step 8: Score editing sites based on coverage and edit %

    * Boyko's confidence scoring using an inverse probability model.

    :param alfa: int
        add A pseudocount
    :param beta: int
        add G pseudocount
    :param cov_margin: float
        minimum allowable edit fraction
    :param keep_all_edited: boolean
        report 100% edited sites
    :param eff_file:
        input vcf or snpEFF (vcf format) file
    :param outfile:
        output conf (vcf format) file
    :return:

    """
    print("Ranking Editing Sites: {}".format(eff_file))

    o = open(outfile, 'w')
    ob = open(os.path.splitext(outfile)[0] + '.bed', 'w')
    # ov = open(os.path.splitext(outfile)[0] + '.vcf', 'w')
    with open(eff_file, 'r') as f:
        for eff in f:
            if eff.startswith("\#\#") or eff.startswith("##"):
                pass
                # ov.write(eff)
            elif eff.startswith("#CHROM"):  # ammend header of EFF file
                # TODO: implement VCF file
                line = eff.split("\t")  # to contain extra numeric columns
                line[2] = "NUM_READS"
                line[5] = "PRE_PSEUDOCOUNT_EDIT%"
                line.insert(5, "POST_PSEUDOCOUNT_EDIT%")
                line.insert(5, "CONFIDENCE")
                o.write('\t'.join(line))
                # ov.write(eff)
            else:
                to_string = process(
                    alfa, beta, cov_margin, keep_all_edited, eff
                )
                ob.write(as_bed(to_string, ct, gt))
                # ov.write(as_vcf(to_string))
                o.write(to_string)
    o.close()
    ob.close()
    # ov.close()


def main(argv=None):  # IGNORE:C0111
    """
    Command line options.
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
        dest="input_eff",
        help="variant eff(vcf) file for filtering",
        required=True
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_conf",
        help="output noSNP (vcf) file with known snps removed.",
        required=True
    )
    parser.add_argument(
        "-c", "--cov_margin",
        dest="cov_margin",
        help="minimum edit fraction",
        required=False,
        default=0.01,
        type=float
    )
    parser.add_argument(
        "-a", "--alpha",
        dest="alpha",
        help="alpha parameter",
        required=False,
        default=0,
        type=int
    )
    parser.add_argument(
        "-b", "--beta",
        dest="beta",
        help="beta parameter",
        required=False,
        default=0,
        type=int
    )
    parser.add_argument(
        "--keep-100-edited",
        dest="keep100",
        help="keep 100 percent edited sites (by default, these are tossed as SNPs)",
        required=False,
        default=False,
        action='store_true'
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
    input_eff = args.input_eff
    outfile = args.output_conf
    cov_margin = args.cov_margin
    alpha = args.alpha
    beta = args.beta
    keep_all_edited = args.keep100
    ct = args.ct
    gt = args.gt
    #

    rank_edits(alpha, beta, cov_margin, keep_all_edited, input_eff, outfile, ct, gt)
    return 0



if __name__ == "__main__":
    sys.exit(main())
