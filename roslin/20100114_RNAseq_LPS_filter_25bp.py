#!/usr/bin/python

## ---------------------------[ pairend_filter.py ]----------------------------
"""  
Reads the two fastq files of a pair end sequence library (Solexa) to filter
out low quality reads.

Filter applied: Tolerate n_low_quality base quality below a given threshold 
(min_trim_q). If a second low-quality base is encouneterd (reading the reads 
5' -> 3'), chop away the read from the 2nd low quality base onward.
Also remove reads short than min_length.
Reads must be present in either both or none libraries. I.e. if a read is 
removed from one library remove the mate from the other library.
"""
## --------------------------------[ User's input ]----------------------------

pair_end_file_1 = 'C:/Tritume/s_7_1_sequence.txt' ## Raw fastq files
pair_end_file_2 = 'C:/Tritume/s_7_2_sequence.txt'

min_trim_q = 20 ## Minimum quality after which trimming will occur

min_length = 25 ## Discard (filtered) reads when shorter than min_length bases

n_low_quality = 2 ## Number of low quality bases (as defined in min_trim_q) 
                  ## allowed before trimming the sequence.

same_length_pe = True ## Should the two reads in a pair be the same length? If 
                      ## True, the longer read will be trimmed. 
                      ## Note: TopHat requires same length.
                  
## Output files are in the same dir as the input.
## Output name: input filename + '.filtered' (e.g. s_7_1_sequence.txt.filtered)


## --------------------------[ Define trim_sequence filterer]------------------

## trim_sequence takes a string of Solexa base quality scores ('aaaBB]]]...')
## and return the second index where quality drops below a certain threshold
## (low_q)

## E.g.
## trim_sequence('aaaaBaaaBBBBBB', 20)
## returns--> 8 (i.e. the length of 'aaaaBaaa')

def trim_sequence(seq_quality, min_trim_q):
    seq_quality = [ord(x) - 64 for x in seq_quality]
    low_q = 0     
    for i in range(0, len(seq_quality)):
        ## Scan the sequence quality to find where quality drops below the threshold
        if seq_quality[i] < min_trim_q:
            low_q += 1
            
        ## At the Nth drop, trim the sequence
        if low_q == n_low_quality + 1:
            seq_trimmed = seq_quality[0 : i]
            ## If the last base has quality below the threshold, drop it
            if seq_trimmed[-1] < min_trim_q:
                seq_trimmed = seq_trimmed[:-1]
            break
    try:
        return(len(seq_trimmed))
    except:
        return(len(seq_quality))

## ----------------------------------------------------------------------------

## Open pair-end files
pe1= open(pair_end_file_1, 'r')
pe2= open(pair_end_file_2, 'r')

## Open output files
pe1_out= open(pair_end_file_1 + '.filtered', 'w')
pe2_out= open(pair_end_file_2 + '.filtered', 'w')

counter = 1 ## This counter used to convert each read (4 lines) to a list

read_pe1 = list() ## List to contain a 4-lines bloc (one read)
read_pe2 = list()

i = 0
line = 'file_iterator'

while line != '':
       
    ## --------------------[ Convert reads (4 line bloc) to list ]-------------
    while counter <= 4:
        line = (pe1.readline()).rstrip('\n')
        read_pe1.append(line)
        
        line = (pe2.readline()).rstrip('\n')
        read_pe2.append(line)

        i += 1         
        counter += 1
    counter = 1

    ## ---------------------------[ End of converter ]-------------------------

    if i % 1000000 == 0:
        print('Processing ' + str(i) + ' lines')
    
    ## Find where to trim the sequences using trim_sequence()
    pe1_trim = trim_sequence(read_pe1[3], min_trim_q)
    pe2_trim = trim_sequence(read_pe2[3], min_trim_q)

    ## Check the length of the trimmed reads.
    ## If one of the two in the pair is too short, drop both (i.e. continue to next read)
    if pe1_trim < min_length or pe2_trim < min_length:
        read_pe1 = list()
        read_pe2 = list()
        continue
    
    ## If one read in a pair is shorter, trim the longer (if same_length_pe was set to True)
    if same_length_pe is True:
        if pe1_trim > pe2_trim:
            pe1_trim = pe2_trim
        else:
            pe2_trim = pe1_trim
    
    ## Return trimmed reads
                        # Name       # Sequence                 # Comment    # Quality
    read_pe1_trimmed = [read_pe1[0], read_pe1[1][0 : pe1_trim], read_pe1[2], read_pe1[3][0 : pe1_trim]]
    read_pe2_trimmed = [read_pe2[0], read_pe2[1][0 : pe2_trim], read_pe2[2], read_pe2[3][0 : pe2_trim]]

    ## Check consistency of names bewteen pair reads (just in case)
    if read_pe1[0][:-2] != read_pe2[0][:-2]:
        print('Inconsistency of names for reads at line ' + str(i))
        print('Read from file 1:\n' + read_pe1_trimmed)
        print('Read from file 2:\n' + read_pe2_trimmed)
        break
    
    ## Write out reads    
    pe1_out.write('\n'.join(read_pe1_trimmed) + '\n')
    pe2_out.write('\n'.join(read_pe2_trimmed) + '\n')

    ## Reset     
    read_pe1 = list()
    read_pe2 = list()

pe1.close()
pe2.close()
pe1_out.close()
pe2_out.close()

## -----------------------------[ Tritume ]------------------------------------
def line_counter(file):
    f = open(file) 
    i = 0
    for line in f:
        i += 1
    f.close()
    return(i)