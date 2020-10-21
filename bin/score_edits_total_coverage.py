#!/usr/bin/env python
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import concurrent.futures
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import matplotlib.pyplot as plt
import pyBigWig
import numpy as np
import pandas as pd
import os
import glob
import pybedtools
import gffutils
from Bio import SeqIO
from tqdm import trange
from collections import defaultdict, OrderedDict
pd.options.mode.chained_assignment = None  # default='warn'
import sys

class Density:
    def values(self, chrom, start, end, strand):
        return 0
    
class ReadDensity(Density):
    """
    ReadDensity class
    Attributes:
        self.pos(positive *.bw file)
        self.neg(negative *.bw file)
    """

    def __init__(self, pos, neg, name=None):
        try:
            self.pos = pyBigWig.open(pos)
            self.neg = pyBigWig.open(neg)
            self.name = name if name is not None else pos.replace(
                'fwd', '*'
            ).replace(
                'rev', '*'
            )

        except Exception as e:
            print("couldn't open the bigwig files!")
            print(e)

    def values(self, chrom, start, end, strand):
        """
        Parameters
        ----------
        chrom : basestring
            (eg. chr1)
        start : int
            0-based start (first position in chromosome is 0)
        end : int
            1-based end (last position is not included)
        strand : str
            either '+' or '-'
        Returns
        -------
        densites : list
            values corresponding to density over specified positions.
        """

        try:
            if strand == "+":
                return list(pd.Series(self.pos.values(chrom, start, end)).fillna(0))
            elif strand == "-":
                return list(pd.Series(self.neg.values(chrom, start, end)).fillna(0))
            else:
                print("Strand neither + or -")
                return 1
        except RuntimeError:
            # usually occurs when no chromosome exists in the bigwig file
            return list(pd.Series([np.NaN] * abs(start - end)).fillna(0))

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def get_c_positions_and_coverage_in_window(bedtool, rdd, genome_fa):
    """
    Given a bedtool (BedTool) of regions, return the positions (0-based) of C's (or G's on neg strand).
    NOTE: Only works with one continuous window. Will break if there is more than one interval. 
    """
    try:
        assert bedtool.to_dataframe().shape[0] == 1
    except AssertionError:
        print("This function does not work with multiple regions: {}".format(bedtool.to_dataframe()))
        sys.exit(1)
        
    d = {}
    pos = bedtool.to_dataframe().iloc[0]
    chrom = pos.chrom
    start = pos.start
    end = pos.end
    strand = pos.strand
    # print("{}:{}-{}:{}".format(chrom, start, end, strand))
    sequences = bedtool.sequence(fi=genome_fa, s=False, name=True) 
    # print(sequences)
    with open(sequences.seqfn) as f:
        for record in SeqIO.parse(f, "fasta"):
            # print(record.seq.upper())
            if strand == '+':
                relpos = find(record.seq.upper(), 'C')
            elif strand == '-':
                relpos = find(record.seq.upper(), 'G')
            else:
                print("Strand error: {}".format(strand))
                sys.exit(1)
    abspos = ["{}:{}".format(chrom, start + p) for p in relpos]
    coverage = rdd.values(chrom=chrom, start=start, end=end, strand=strand)
    coverage = [np.abs(c) for c in coverage]  # doesn't matter for how we're making bigwigs, but just to be sure. 
    c_coverage = [coverage[p] for p in relpos]
    for p, c in zip(abspos, c_coverage):
        d[p] = c
    return d


def get_total_c_coverage(row, rdd, genome_fa):
    """
    Just wraps sum_all_c_coverage_in_window() to work with pandas row
    """
    bedtool = pybedtools.BedTool(
        [pybedtools.create_interval_from_list(
            [row['chrom'], row['start'], row['end'], "window", "0", row['strand']]
        )]
    )
    return sum_all_c_coverage_in_window(bedtool, rdd, genome_fa)


def sum_all_c_coverage_in_window(bedtool, rdd, genome_fa):
    all_coverage = 0
    c_positions = get_c_positions_and_coverage_in_window(bedtool, rdd, genome_fa)
    for pos, cov in c_positions.items():
        all_coverage += cov
    return int(all_coverage)


## helper func
def get_gene_positions_dict(db):
    """
    Returns the genic positions for each gene in a gencode annotation database.
    ie. {"gene_id":{'chrom':chr1,'start':0,'end':100,'strand':"+"}}
    """
    gene_positions = defaultdict()
    genes = db.features_of_type('gene')
    for gene in genes:
        gene_id = gene.attributes['gene_id'][0] if type(gene.attributes['gene_id']) == list else gene.attributes['gene_id']
        gene_positions[gene_id] = {'chrom':gene.seqid, 'start':gene.start-1, 'end':gene.end, 'strand':gene.strand}
    return gene_positions

def read_and_filter_editing_sites(sites_file, conf, v=False):
    annotated_headers = [
        'chrom','start','end','conf','edit_frac','strand',
        'gene_id','gene_name','region','annotation_string'
    ]
    sites = pd.read_csv(sites_file, names=annotated_headers, sep='\t')
    if v:
        print("before confidence filtering: ",sites.shape[0])

    sites = sites[sites['conf'] >=conf]
    # sites = sites[['chrom','start','end','edit_frac','gene_id','region','strand']]
    if v:
        print("after confidence filtering: ",sites.shape[0])
    return sites

## pilot window func

def create_chrom_sizes_dict(chrom_sizes):
    """
    Creates a chrom sizes dictionary. Useful for identifying 
    chromosomal boundaries in which we cannot exceed.
    """
    chrom_sizes_dict = {}
    with open(chrom_sizes, 'r') as f:
        for line in f:
            chrom, size = line.strip('\n').split('\t')
            chrom_sizes_dict[chrom] = int(size)
    return chrom_sizes_dict

def create_window_interval(center_site, flank, chrom_sizes_dict):
    """
    Given a position (center_site), and a flanking distance,
    return a window interval.
    window size will be flank + 1 + flank (ie. 2 + 1 + 2 = 5 if flank = 2)
    """
    window_start = center_site.start - flank
    window_start = 0 if window_start < 0 else window_start
    
    window_end = center_site.start + flank + 1
    window_end = chrom_sizes_dict[center_site.chrom] if window_end > chrom_sizes_dict[center_site.chrom] else window_end
    
    return pybedtools.create_interval_from_list(
        [
            center_site.chrom, 
            str(window_start), 
            str(window_end), 
            center_site.name, 
            center_site.score, 
            center_site.strand
        ]
    )

def create_window_intervals(sites, flank, chrom_sizes_dict):
    windows = []
    for site in sites:
        windows.append(create_window_interval(site, flank, chrom_sizes_dict))
    return pybedtools.BedTool(windows)


def score_edits(annotated_edits_file, bg_edits_file, output_file, conf, gene_positions_dict, genome_fa, flank, chrom_sizes_file, rdd):
    """
    1. Reads and filters our (annotated) editing site (fg). The "name" (edit_frac) MUST contain the edited,totalcov for each site.
    2. Creates a bedtools interval (interval) containing gene coordinates. 
    3. Subsets our (annotated) editing list (fg) to get only the edits across one gene, for every gene. If a gene has no edit sites, pass. 
        A. For this step, we're relying on what's been annotated by annotator. So we are only counting edits that are unambiguously assigned
           (edits at a given position that overlaps multiple genes in the same region are not counted). 
    4. Filter out bg_edits_file from fg_edits_file. 
    5. Open a window centered around every edit site.
    6. Intersect with all edits from (3) to collect all edits that exist within the window.
    7. Add up all the edited-reads and total-reads across edited sites and calculate the "edit/editedc" fraction.
    8. Calculate the coverage across all C's in each window
    """
    
    chrom_sizes_dict = create_chrom_sizes_dict(chrom_sizes_file)
    # (1) Reads and filters our (annotated) editing site (fg). This file MUST have a conf value in the 4th column. 
    fg = read_and_filter_editing_sites(annotated_edits_file, conf)
    progress = trange(len(set(fg['gene_id'])))
    all_scores_df = pd.DataFrame(
        columns = [
            'chrom','start','end','name','score',
            'strand','edit_coverage','editable_coverage',
            'edited_over_edited_c','all_c_coverage','edited_over_all_c'
        ]
    )
    all_scores = []
    for gene_id in set(fg['gene_id']):
        try:
            # (2) Creates a bedtools interval (interval) containing gene coordinates. 
            interval = pybedtools.create_interval_from_list([
                gene_positions_dict[gene_id]['chrom'],
                gene_positions_dict[gene_id]['start'],
                gene_positions_dict[gene_id]['end'],
                gene_id,
                '0',
                gene_positions_dict[gene_id]['strand'],
            ])
            # (3) Subsets our (annotated) editing list (fg) to get only the edits across one gene, for every gene. 
            fg_sites_in_region = fg[fg['gene_id']==gene_id]
            
            
            if fg_sites_in_region.shape[0] >= 1:
                
                # thickStart = edited #
                fg_sites_in_region.loc[:,'thickStart'] = fg_sites_in_region['edit_frac'].apply(
                    lambda x: int(x.split(',')[0])
                )
                # thickEnd = total coverage # 
                fg_sites_in_region.loc[:,'thickEnd'] = fg_sites_in_region['edit_frac'].apply(
                    lambda x: int(x.split(',')[1])
                )
                fg_sites_in_region.loc[:,'name'] = fg_sites_in_region.loc[:,'gene_id'] + \
                    "|" + fg_sites_in_region.loc[:,'region']
                fg_sites_in_region = fg_sites_in_region[
                    ['chrom','start','end','name','conf','strand','thickStart','thickEnd']
                ]
                
                # (4) Filter out bg_edits_file from fg_edits_file. 
                fg_prefiltered_sites_bedtool = pybedtools.BedTool.from_dataframe(fg_sites_in_region) 
                if bg_edits_file is not None:
                    bg_sites_bedtool = pybedtools.BedTool(bg_edits_file)
                    fg_sites_bedtool = fg_prefiltered_sites_bedtool.sort().intersect(bg_sites_bedtool.sort(), s=True, v=True)
                else:
                    fg_sites_bedtool = fg_prefiltered_sites_bedtool
                if len(fg_sites_bedtool) > 0: # If the background file totally removes all edits from the foreground file, we might get an EmptyDataFrame
                    # (5) Open a window centered around every edit site.
                    fg_windows_bedtool = create_window_intervals(fg_sites_bedtool, flank, chrom_sizes_dict)

                    # (6) Intersect with all edits from (3) to collect all edits that exist within the window.
                    intersected_edits = fg_windows_bedtool.intersect(
                        fg_sites_bedtool, s=True, wa=True, loj=True
                    ).to_dataframe(
                        names=[
                            'chrom','start','end','name','score','strand',
                            'edit_chrom','edit_start','edit_end','edit_name',
                            'edit_score','edit_strand','edit_coverage','editable_coverage'
                        ]
                    )
                    # (7) Add up all the edited-reads and total-reads across edited sites and calculate the "edit/editedc" fraction.
                    summed_confs = pd.DataFrame(
                        intersected_edits.groupby(
                            ['chrom','start','end','name','score','strand']
                        )['edit_score'].sum()
                    ).reset_index()

                    # blockCount is the "number of reads supporting an edit site"
                    summed_edits = pd.DataFrame(
                        intersected_edits.groupby(
                            ['chrom','start','end','name','score','strand']
                        )['edit_coverage'].sum()
                    ).reset_index()
                    # editable_coverage (blockSizes) is the "total number of reads at the edited site"
                    summed_total_coverage = pd.DataFrame(
                        intersected_edits.groupby(
                            ['chrom','start','end','name','score','strand']
                        )['editable_coverage'].sum()).reset_index()
                    df = pd.merge(
                        summed_edits, 
                        summed_total_coverage, 
                        how='outer', 
                        left_on=['chrom','start','end','name','score','strand'],
                        right_on=['chrom','start','end','name','score','strand']
                    )
                    df['edited_over_edited_c'] = df['edit_coverage']/df['editable_coverage']

                    # (8) Calculate the coverage across all C's in each window
                    df['all_c_coverage'] = df.apply(get_total_c_coverage, args=(rdd, genome_fa, ), axis=1)
                    df['edited_over_all_c'] = df['edit_coverage']/df['all_c_coverage']

                    # reorder columns to match
                    df = df[[
                        'chrom','start','end','name','score',
                        'strand','edit_coverage','editable_coverage',
                        'edited_over_edited_c','all_c_coverage','edited_over_all_c'
                    ]]
                    all_scores.append(df)
                    # all_scores = pd.concat([all_scores, df])
            pybedtools.cleanup()        
        except KeyError as e:
            pass
        progress.update(1)
        
    for score_df in all_scores:
        all_scores_df = pd.concat([all_scores_df, score_df])
    all_scores_df.sort_values(by=['chrom','start','end','strand']).to_csv(
        output_file, 
        sep='\t', 
        index=False, 
        header=True
    )
    
def main():
    parser = ArgumentParser(
        description="Creates windows surrounding edit sites and calculates the read coverage across edits and editable sites."
    )
    parser.add_argument(
        "--annotated_edits_file", 
        help="input file from joined edits (conf score should be 4th column, \
        it should be annotated using my annotator script.)", 
        required=True, 
        default=None
    )
    parser.add_argument(
        "--bg_edits_file", 
        help="background edits we want to subtract.", 
        required=False, 
        default=None
    )
    parser.add_argument("--conf", help="conf score", required=False, type=float, default=0.)
    parser.add_argument(
        "--flank", 
        help="half the window size +1 (default: 25, so default window size \
        is 25 + 1 + 25 = 51)", 
        required=False, 
        type=int, 
        default=25
    )
    parser.add_argument("--gtfdb", help="GFFUtils DB file", required=True, default=None)
    parser.add_argument("--output_file", help="output bedfile", required=False, default=None)
    parser.add_argument("--genome_fa", help="genome fasta file", required=True, default=None)
    parser.add_argument("--chrom_sizes_file", help="genome chrom.sizes file", required=True, default=None)
    parser.add_argument("--pos_bw", help="bigwig file (positive)", required=True, default=None)
    parser.add_argument("--neg_bw", help="bigwig file (negative)", required=True, default=None)
    args = parser.parse_args()
    annotated_edits_file = args.annotated_edits_file
    bg_edits_file = args.bg_edits_file
    conf = args.conf
    flank = args.flank
    gtfdb = args.gtfdb
    pos_bw = args.pos_bw
    neg_bw = args.neg_bw
    
    rdd = ReadDensity(
        pos=pos_bw,
        neg=neg_bw,  
    )
    
    output_file = "{}.{}.flank{}.bed".format(
        annotated_edits_file,
        conf,
        flank,
    ) if args.output_file is None else args.output_file
    
    genome_fa = args.genome_fa
    chrom_sizes_file = args.chrom_sizes_file
    db = gffutils.FeatureDB(gtfdb)
    gene_positions_dict = get_gene_positions_dict(db)
    
    score_edits(
        annotated_edits_file=annotated_edits_file, 
        bg_edits_file=bg_edits_file,
        output_file=output_file, 
        conf=conf, 
        gene_positions_dict=gene_positions_dict,
        genome_fa=genome_fa,
        flank=flank,
        chrom_sizes_file=chrom_sizes_file,
        rdd=rdd
    )
    
if __name__ == '__main__':
    main()
