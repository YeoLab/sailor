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
import pybedtools as bt
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

def is_intergenic(row):
    """
    A genic region is defined as either: 
        1) an intron
        2) an exon (5' UTR, CDS, 3' UTR)
    is_intergenic determines if a row (from a bedtools closest result) 
    lies within genic regions. Returns the region name if genic, otherwise
    returns 'intergenic|whatever the closest genic region is'
    """
    if row['distance_from_region'] > 0:
        return "intergenic|{}".format(row['region_name'])
    else:
        return row['region_name']

def priority(row):
    """
    If there are overlapping annotations in the gff file, we will prioritize 
    regions our SNV is contained in:
        1) 3' UTR
        2) 5' UTR
        3) CDS
        4) Intron
    Returns an assigned priority 
    """
    if row['region'] == 'three_prime_UTR':
        return 1
    elif row['region'] == 'five_prime_UTR':
        return 2
    elif row['region'] == 'CDS':
        return 3
    elif row['region'] == 'Intron':
        return 4

def conf_to_bed(conf_file, output_bedfile, min_confidence):
    """
    Step 9: Converts a "conf" file (vcf format) into a bedfile.
    """
    print("Converting conf files to bedfiles: {}".format(conf_file))
    bedfile = open(output_bedfile,'w')
    with open(conf_file,'r') as f:
        for line in f:
            strand = '.'
            if not line.startswith('#'):
                line = line.split('\t')
                if line[3] == 'A':
                    strand = '+'
                elif line[3] == 'T':
                    strand = '-'
                if float(line[5]) >= min_confidence:
                    bedfile.write("{0}\t{1}\t{2}\t{3:.2f}\t{4}\t{5}\n".format(line[0],
                                                                          int(line[1])-1,
                                                                          int(line[1]),
                                                                          int(float(line[7])*100),
                                                                          line[2],
                                                                          strand))
    bedfile.close()

def annotate_bed(input_bedfile, output_bedfile, gff3):
    
    """
    Step 10: Given a bedfile and annotation gff3, annotate regions.
    """
    print("Annotating: {}".format(input_bedfile))
    genes = bt.BedTool(gff3)
    conf = bt.BedTool(input_bedfile)
    annotations = conf.closest(genes, d=True).to_dataframe(names=['chrom',
                                                                  'pos-1',
                                                                  'pos',
                                                                  'approx_edit_fraction',
                                                                  'approx_coverage',
                                                                  'strand',
                                                                  'region_chrom',
                                                                  'source',
                                                                  'region_name',
                                                                  'region_start',
                                                                  'region_end',
                                                                  'region_.',
                                                                  'region_strand',
                                                                  '.',
                                                                  'region_annotation',
                                                                  'distance_from_region'])
    annotations['region'] = annotations.apply(is_intergenic,axis=1)
    del annotations['region_name'] # delete this as 'region' effectively replaces it.
    annotations['priority'] = annotations.apply(priority,axis=1)
    annotations.sort_values(by=['priority'])
    annotations.drop_duplicates(subset=['chrom',
                                        'pos-1',
                                        'pos',
                                        'approx_coverage',
                                        'approx_edit_fraction',
                                        'strand'],
                                inplace=True)
    del annotations['priority'] # not part of a proper bedfile
    del annotations['region_.'] # not part of a proper bedfile
    del annotations['.'] # not part of a proper bedfile
    annotations['region_annotation'] = annotations['region_annotation'].str.replace('Parent=Transcript:','')
    # annotations = annotations[annotations['pos'].isin(falsepositives)==False]
    annotations.to_csv(output_bedfile,sep="\t",header=True,index=None)
      
    
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
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument("-i", "--input", dest="conf", help="confidence (vcf) file for conversion to bed", required = True)
        parser.add_argument("-o", "--output", dest="bed", help="output bedfile", required = True)
        parser.add_argument("-c", "--confidence", dest="confidence", help="confidence threshold cutoff", required = False, default = 0.995, type = float )
        parser.add_argument("-g", "--gff3", dest="gff3", help="gff3 annotation file", required = True )
        
        # Process arguments
        args = parser.parse_args()
        conf_file = args.conf
        bedfile = args.bed
        min_confidence = args.confidence
        gff3 = args.gff3
                
        conf_to_bed(conf_file, bedfile.replace('.bed','.unannotated.bed'), min_confidence)
        annotate_bed(bedfile.replace('.bed','.unannotated.bed'), bedfile, gff3)
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
