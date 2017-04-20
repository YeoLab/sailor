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
import re
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

def vcf2eff(input_vcf, output_eff, min_coverage):
    """
    Step 6: Filter variants for coverage and editing-specific AG/TC changes.

    Converts vcf file into an "eff" file (essentially filtering for variants at this step).

    :param input_vcf: basestring
        vcf-formatted file
    :param output_eff: basestring
        vcf-formatted file
    :param min_coverage: int
        minimum coverage required to call a variant
    :return:
    """

    print("Calling vcf2eff: {}".format(input_vcf))
    o = open(output_eff,'w')
    with open(input_vcf) as f:
        # for line in f:
        for line in f:
            flag = 1  # if flag remains at 1 throughout filter, this is a 'good' read to keep
            
            if line.startswith('#'):  # is vcf header
                o.write(line)
            else:
                line = line.split('\t')
                ref = line[3]
                alt = line[4]
                
                dp, i = re.findall('DP\=(\d+)\;.*DP4\=([\d\,]+)', line[7])[0]
                """
                if the DP flag does not meet minimum coverage, toss it.
                """
                i = i.split(',')
                if int(dp) < min_coverage:
                    flag = 0
                
                """
                i[0] = forward ref allele
                i[1] = reverse ref allele
                i[2] = forward non-ref allele
                i[3] = reverse non-ref allele
                
                logic: if there are more ref/non-ref alleles on the reverse strand, 
                is it 'reversed' due to TruSeq stranded preparation.
                
                """
                
                
                if (int(i[0]) + int(i[2])) < (int(i[1]) + int(i[3])):
                    sense = True
                    refNum = int(i[1])
                    altNum = int(i[3])
                else: 
                    sense = False
                    refNum = int(i[0])
                    altNum = int(i[2])
                
                """
                Get edit percentage 
                """
                if(altNum + refNum) > 0:
                    line[5] = str(altNum / float(altNum + refNum))
                    line[2] = str(altNum + refNum)
                    
                    eff = re.findall('EFF=([^\(]+)',line[7])
                    if len(eff) > 0:
                        line[6] = eff # post filtering step after snpEff
                
                """
                # 6) if not A-G or T-C, then pass
                
                """
                if((ref == 'A' and alt.find('G')==-1) or (ref == 'T' and alt.find('C')==-1)):
                    flag = 0
                    
                """
                # 6) if reference isn't A (forward) or T (reverse), toss it
                """
                if ((sense and ref != 'A') or (not sense and ref != 'T')) :
                    flag = 0
                
                """
                if vcf line survives all filters, write it.
                """
                if flag == 1:
                    newline = "\t".join([l for l in line])
                    o.write(newline)
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
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
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
            required = True
        )
        parser.add_argument(
            "-o", "--output",
            dest="output_eff",
            help="output vcf (eff) filtered per editing rules",
            required = True
        )
        parser.add_argument(
            "-m", "--min_coverage",
            dest="min_coverage",
            help="minimum allowable read coverage to pass variant filter",
            required = False,
            type=int,
            default = 10
        )
        # Process arguments
        args = parser.parse_args()
        input_vcf = args.input_vcf
        output_eff = args.output_eff
        
        min_coverage = args.min_coverage
        
        vcf2eff(input_vcf, output_eff, min_coverage)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
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
