#!/usr/bin/env python
# encoding: utf-8
'''
Combines stranded edits BED files and re-calculates coverages. 

@author:     Brian Yee

@copyright:  2020 Yeolab. All rights reserved.

@license:    license

@contact:    bay001@ucsd.edu
@deffield    updated: 9-16-2020
'''

import sys
import glob
import os
import glob
import pandas as pd
import numpy as np

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2020-09-16'
__updated__ = '2020-09-16'

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
    

def concat_bedfiles(fwd_file, rev_file):
    """
    Combines two native SAILOR fwd and rev bedfiles
    """
    common_header = ['chrom','start','end','info','conf','strand']
    fwd = pd.read_csv(fwd_file, sep='\t', names=common_header)
    rev = pd.read_csv(rev_file, sep='\t', names=common_header)
    return pd.concat([fwd, rev])


def get_number_edited_reads(row):
    """
    SAILOR reports the total coverage and edit fraction in the 'info' column.
    Use these two numbers to get the number of edited reads.
    """
    total_reads, edit_type, fraction = row['info'].split('|')
    return round(int(total_reads) * float(fraction))


def label_cov_info(row):
    """
    returns the num_edited and total_coverage as a concatenated string.
    """
    return "{},{}".format(row['num_edited'], row['total_coverage'])


def combine_and_reformat(fwd, rev, output, force_rewrite=True):
    if not os.path.exists(output) or force_rewrite:
        df = concat_bedfiles(fwd_file=fwd, rev_file=rev)
        df['total_coverage'] = df['info'].apply(lambda x: int(x.split('|')[0]))
        df['num_edited'] = df.apply(get_number_edited_reads, axis=1)
        df['name_col'] = df.apply(label_cov_info, axis=1)
        df[['chrom','start','end','conf','name_col','strand']].to_csv(
            output, 
            sep='\t', 
            index=False, 
            header=False
        )
    else:
        print("{} exists, use --force to force override.")


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

  Created by Brian Yee on %s.
  Copyright 2020 Yeo lab. All rights reserved.

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
            "-f", "--fwd",
            dest="fwd",
            help="plus-strand edits file",
            required=True
        )
        parser.add_argument(
            "-r", "--rev",
            dest="rev",
            help="minus-strand edits file",
            required=True
        )
        parser.add_argument(
            "-o", "--output",
            dest="output",
            default=None,
            help="output file",
            required=False
        )
        parser.add_argument(
            "--force",
            dest="force",
            default=False,
            action='store_true',
            required=False
        )
        # Process arguments

        args = parser.parse_args()
        fwd = args.fwd
        rev = args.rev
        force_rewrite = args.force
        output = args.output if args.output is not None else fwd.replace(
            '.fwd.sorted.rmdup.readfiltered.formatted.varfiltered.snpfiltered.ranked','.combined'
        )
        # print("OUTPUT: {}".format(output))
        # Call function
        combine_and_reformat(
            fwd=fwd,
            rev=rev, 
            output=output, 
            force_rewrite=force_rewrite
        )

    except Exception as e:
        print("Exception in main: {}".format(e))
        exit(1)



if __name__ == "__main__":
    sys.exit(main())
