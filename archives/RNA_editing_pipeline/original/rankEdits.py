import sys
import math

import scipy
from scipy.special import betainc

import re

def readLine(line):
#    sys.stderr.write(line)

    # parse EFF format
    # print(line)
    (chr, pos, dot, ref, alt, qual, #) = line.split("\t")[:5]
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
    
    dp4 = re.findall("DP4\=([\d\,]+)",info)[0]


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
    confidence = 1 - scipy.special.betainc(G, A, cov_margin)

    # retrieve genic region found by snpEff
    region = "NoRegion"
    if len(infos) > 2:
        eff = infos[-1]
        if eff[:3] == "EFF":
            regions = set([ region.split("(")[0] for region in eff[4:].split(",") if region.split("(")[0] != 'UPSTREAM' and region.split("(")[0] != 'DOWNSTREAM'] )
            # report only most interesting region for each site:
            priorities = ["SPLICE_SITE_ACCEPTOR", "SPLICE_SITE_DONOR", "NON_SYNONYMOUS_CODING", "SYNONYMOUS_CODING", "UTR_3_PRIME", "EXON", "INTRON", "UTR_5_PRIME"]
            for x in priorities:
                if x in regions:
                    region = x
                    break


    # print line in CONF format
    if confidence > conf_min:
        print "\t".join([chr, pos, str(num_reads), ref, alt, ""]),
        print "\t".join(str(round(y,9)) for y in [confidence, theta, edit_frac]),
        print "\t".join(["", region, info, format, cond])
    
# Main Function
if __name__ == "__main__":
    # get pseudocounts alfa(G) and beta(A)
    # and coverage margin from command line
    alfa = int(sys.argv[2]) 
    beta = int(sys.argv[3])
    cov_margin = float(sys.argv[4])
    conf_min = float(sys.argv[5])
    
    eff_file = open(sys.argv[1])
    for eff in eff_file:
        if eff.startswith("\#\#") or eff.startswith("##"):
            pass
        elif eff.startswith("#CHROM"):    # ammend header of EFF file
            line = eff.split("\t")        # to contain extra numeric columns
            sys.stderr.write("\t".join(line))
            line[2] = "NUM_READS"
            line[5] = "EDIT%"
            line.insert(5, "POST_EDIT%")
            line.insert(5, "CONFIDENCE")
            print "\t".join(line),
        else:
            readLine(eff)
        
    
