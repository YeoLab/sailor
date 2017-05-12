use warnings;
$minOverhang = 10;
$minUnderhang = 0;

while (<>) {
    print and next if m/^\@/;
    @F = split /\t/;
    if ($F[5] =~ m/^(\d+)M.*[\D](\d+)M$/) { 
	#print STDERR "short overhang min($1,$2) < $minOverhang\n$_\n" and 
	next if $1<$minOverhang or $2<$minOverhang ; # filter out reads with small overhang
    }
    
    $_ =~ m/MD:Z:([\^\w]+)\t/ ; # replaces: $_ =~ m/MD:Z:(\w+)\t/ ;
    $mm = $1;
    next if $mm =~ m/\d[CG]\d/ or $mm =~ m/\^/ ;
    $sense = ($F[1] & 0x10) > 0; # reads always map reversed to the sense strand
                                 # switch to < when working with TruSeq data, not Balaji's prep
    # filter out reads with mismatch close to end of read
    $mm =~ m/^(\d+).*[ACGT](\d+)$/ ;
    if ($1 and $2) {
    	next if $1 < $minUnderhang or $2 < $minUnderhang ;
	}
	else {
		next if $1 < $minUnderhang;
	}
    $flag = 1; $seq = $F[9];
    while ($mm =~ s/^(\d+)([AT])//) { 
	$ref = $2;
	$read = substr($seq,$1,1);
	
	
	$flag = 0 and last if not (($ref eq "A" and $read eq "G" and $sense) or ($ref eq "T" and $read eq "C" and not $sense)); 
	$seq = substr($seq,1+$1) ; 
    }
    print if $flag ;
}

# Use of uninitialized value $mm in pattern match (m//) at /home/yeo-lab/software/RNA_editing/filterNonAG.pl line 15 
# when MD:Z:
