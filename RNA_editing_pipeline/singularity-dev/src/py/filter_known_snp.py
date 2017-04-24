#!/usr/bin/env python
# encoding: utf-8
'''
editing.filter_known_snps

removes known SNPs (BED3) from a candidate list of editing sites (VCF).

@author:     brian

@copyright:  2017 yeolab. All rights reserved.

@license:    license

@contact:    bay001@ucsd.edu
@deffield    updated: 4-21-2017
'''

import sys
import os
import pandas as pd

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


def filter_known_snp(infile, known, outfile):
    """
    Step 7: Remove known SNPs

    We don't want to erroneously call editing sites that are known SNPs.
    Filter these out with a BED3 file with known SNP locations.
    Really just compares the 0-based position of the BED3 file with the
    1-based position of the vcf file, and filters accordingly.

    :param infile: basestring
        file location of the input VCF file
    :param known: basestring
        file location of the BED3 file containing known SNPs
    :param outfile: basestring
        file location of the intended output VCF file
    :return:
    """

    # print("Filtering known SNPs: {}".format(infile))
    o = open(outfile, 'w')
    with open(infile, 'r') as f:
        for line in f:
            if line.startswith('#'):
                o.write(line)
    o.close()

    names1 = [
        'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT',
        '.'
    ]
    eff_df = pd.read_table(infile, comment='#', names=names1,
                           dtype={'QUAL': str})

    names2 = ['CHROM', 'START',
              'POS']  # POS is the 1-based position of the SNP.
    if known.endswith('.gz'):
        snp_df = pd.read_table(known, compression='gzip', names=names2)
    else:
        snp_df = pd.read_table(known, names=names2)

    snp_df['KNOWN'] = 1
    joined = pd.merge(eff_df, snp_df, how='left', on=['CHROM', 'POS'])

    # print("Number of known SNPs filtered out: {}".format(
    #     joined[joined['KNOWN']==1].shape[0])
    # )
    keep = joined[joined['KNOWN'] != 1]

    del keep['KNOWN']

    with open(outfile, 'a') as o:
        keep.to_csv(o, header=False, index=False, sep='\t')


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
            dest="input_eff",
            help="variant eff(vcf) file for filtering",
            required=True
        )
        parser.add_argument(
            "-o", "--output",
            dest="output_noSNP",
            help="output noSNP (vcf) file with known snps removed.",
            required=True
        )
        parser.add_argument(
            "-k", "--known",
            dest="known",
            help="bed3 file of known snps",
            required=True
        )
        # Process arguments
        args = parser.parse_args()
        input_eff = args.input_eff
        output_noSNP = args.output_noSNP

        known = args.known

        filter_known_snp(input_eff, known, output_noSNP)
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
