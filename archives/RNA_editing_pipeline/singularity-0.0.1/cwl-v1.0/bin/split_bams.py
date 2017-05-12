#!/usr/bin/env python
# encoding: utf-8
'''
editing.filter_reads -- shortdesc

editing.filter_reads is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2016 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
from tqdm import trange
import pysam

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2016-07-13'
__updated__ = '2016-07-13'

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


def main(argv=None):  # IGNORE:C0111
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
            "-f", "--flags",
            dest="flags",
            help="SAM Flags to KEEP",
            required=True,
            type=int,
            nargs='+',
        )
        # Process arguments

        args = parser.parse_args()
        input_bam = args.input_bam
        output_bam = args.output_bam
        flags = args.flags

        i = pysam.AlignmentFile(input_bam)
        # if not i.check_index:
        # pysam.index(input_bam)

        o = pysam.AlignmentFile(output_bam, "wb", template=i)
        # progress = trange(i.mapped + i.unmapped)
        for read in i:
            if read.flag in flags:
                o.write(read)
            # progress.update(1)

    except Exception as e:
        print(e)
        exit(1)
    i.close()
    o.close()

if __name__ == "__main__":
    sys.exit(main())