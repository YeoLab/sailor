use strict;
use warnings;

my $minCoverage = $ARGV[$#ARGV];
print STDERR "vcf2eff.pl : minCoverage = $minCoverage\n";

while(<>) {
    my @F = split /\t/;
    print and next if m/^\#/;
    
    my $ref = $F[3];
    $F[4] =~ s/X/$ref/;
    
    my $alt = $F[4];
    	
    # next if not (($ref eq "A" and substr($alt,1) eq ",A") or ($ref eq "T" and substr($alt,1) eq ",T"));
	next if not (($ref eq "A") or ($ref eq "T"));
	
	$F[7] =~ m/DP\=(\d+)\;.*DP4\=([\d\,]+)/ ;
    #$F[7] =~ m/DP\=(\d+)\;I16\=([\d\,]+)/ ;
    my $DP = $1;
    
    my @I = split(",",$2);
    
    next if $DP < $minCoverage;

    # counterintuitively using < for Balaji's first-strand library prep
    my $sense = ($I[0] + $I[2] < $I[1] + $I[3]) ; # change to > for TruSeq
    my $refNum = $sense ? $I[1] : $I[0];
    my $altNum = $sense ? $I[3] : $I[2];
    
    if (($altNum + $refNum) > 0) {
	$F[5] = $altNum / ($altNum+$refNum); 
	$F[2] = $altNum+$refNum; 
	$F[6] = $1 if $F[7] =~ m/EFF=([^\(]+)/;
	print join("\t",@F); # if ($sense and $ref eq 'A') or (not $sense and $ref eq 'T');
    }
}
