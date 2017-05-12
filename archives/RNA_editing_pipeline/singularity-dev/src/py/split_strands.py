#!/usr/bin/env python
# encoding: utf-8
'''
split_strands

Splits a bam file and returns two bam files split on strandedness.

@author:     brian

@copyright:  2017 yeolab. All rights reserved.

@license:    license

@contact:    bay001@ucsd.edu
@deffield    updated: 4-21-2017
'''

import sys
import os
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


def split_strands(input_bam, output_fwd_bam, output_rev_bam, is_reverse):
    """

    :param input_bam: basestring
    :param output_fwd_bam: basestring
    :param output_rev_bam: basestring
    :param is_reverse: boolean
        True if the library is reverse stranded
    :return 0: successful otherwise 1 if exception
    """
    if is_reverse:
        forward_flags = [16, 83, 163]
        reverse_flags = [0, 99, 147]
    else:
        reverse_flags = [16, 83, 163]
        forward_flags = [0, 99, 147]
    try:
        input_handle = pysam.AlignmentFile(input_bam)

        fwd_handle = pysam.AlignmentFile(
            output_fwd_bam, "wb", template=input_handle
        )
        rev_handle = pysam.AlignmentFile(
            output_rev_bam, "wb", template=input_handle
        )

        for read in input_handle:
            if read.flag in forward_flags:
                fwd_handle.write(read)
            elif read.flag in reverse_flags:
                rev_handle.write(read)

        input_handle.close()
        fwd_handle.close()
        rev_handle.close()
        print(output_fwd_bam)
        return 0
    except Exception as e:
        print(e)
        return 1

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
            dest="input_bam",
            help="sorted rmdup bam file for filtering",
            required=True
        )
        parser.add_argument(
            "-f", "--output-forward",
            dest="output_fwd_bam",
            help="output forward strand only bams",
            default="-",
            required=False
        )
        parser.add_argument(
            "-r", "--output-reverse",
            dest="output_rev_bam",
            help="output reverse strand only bams",
            default="-",
            required=False
        )
        parser.add_argument(
            "--reverse-strand",
            action='store_true',
            default=False,
            help="reverse stranded library "
                 "(FWD FLAGS=16, 83, 163) (REV FLAGS=0, 99, 147)",
        )

        # Process arguments

        args = parser.parse_args()
        input_bam = args.input_bam
        is_reverse = args.reverse_strand

        if args.output_fwd_bam is not '-':
            output_fwd_bam = args.output_fwd_bam
        else:
            output_fwd_bam = os.path.splitext(input_bam)[0] + '.fwd.bam'

        if args.output_rev_bam is not '-':
            output_rev_bam = args.output_rev_bam
        else:
            output_rev_bam = os.path.splitext(input_bam)[0] + '.rev.bam'

        # Call function
        split_strands(input_bam, output_fwd_bam, output_rev_bam, is_reverse)

    except Exception as e:
        print(e)
        exit(1)



if __name__ == "__main__":
    sys.exit(main())