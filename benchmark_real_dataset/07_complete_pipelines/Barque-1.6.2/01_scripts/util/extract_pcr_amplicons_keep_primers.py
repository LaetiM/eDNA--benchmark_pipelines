#!/usr/bin/env python3
"""Extract PCR amplicons from fasta sequences using primers

Usage:
    <program> input_fasta left_primer right_primer max_distance min_length max_length output_fasta

Where:
    input_fasta   is a fasta file with DNA sequences <str>
    left_primer   is the DNA sequence of the left primer <str>
    right_primer  is the DNA sequence of the right primer (not reversed or complemented) <str>
    max_distance  is the maximum number differences between the primers and the sequence <int>
    min_length    is the minimum amplicon length desired without the primers <int>
    max_length    is the maximum amplicon length desired without the primers <int>
    output_fasta  is a fasta file containing only the extracted amplicons <str>
"""

# Modules
import sys

# Classes
class Fasta(object):
    """Fasta object with name and sequence
    """

    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence

    def write_to_file(self, handle):
        handle.write(">" + self.name + "\n")
        handle.write(self.sequence + "\n")

    def __repr__(self):
        return self.name + "\t" + self.sequence[0:31]

# Function
def myopen(infile, mode="rt"):
    if infile.endswith(".gz"):
        return gzip.open(infile, mode=mode)
    else:
        return open(infile, mode=mode)

def fasta_iterator(input_file):
    """Takes a fasta file input_file and returns a fasta iterator
    """

    with myopen(input_file) as f:
        sequence = ""
        name = ""
        begun = False

        for line in f:
            line = line.strip()

            if line.startswith(">"):
                if begun:
                    yield Fasta(name, sequence)

                name = line.replace(">", "")
                sequence = ""
                begun = True

            else:
                sequence += line

        if name != "":
            yield Fasta(name, sequence)

def hamming(seq1, seq2, normalized=False):
    """Compute the Hamming distance between the two sequences `seq1` and `seq2`.
    The Hamming distance is the number of differing items in two ordered
    sequences of the same length. If the sequences submitted do not have the
    same length, an error will be raised.
    
    If `normalized` evaluates to `False`, the return value will be an integer
    between 0 and the length of the sequences provided, edge values included;
    otherwise, it will be a float between 0 and 1 included, where 0 means
    equal, and 1 totally different. Normalized hamming distance is computed as:
    
        0.0                         if len(seq1) == 0
        hamming_dist / len(seq1)    otherwise
    """
    seq1_len = len(seq1)
    seq2_len = len(seq2)
    if seq1_len != seq2_len:
        raise ValueError("expected two strings of the same length")

    if seq1_len == 0:
        return 0.0 if normalized else 0  # equal

    distance = sum(c1 != c2 for c1, c2 in zip(seq1, seq2))

    if normalized:
        return distance / float(seq1_len)

    else:
        return distance

def hamming_find(query, text, max_distance=3):
    """Find position of query with a minimal hamming distance
    """
    position = -1
    min_distance = max_distance + 1

    for i in range(len(text) - len(query) + 1):
        subset = text[i: i + len(query)]
        distance = hamming(query, subset)

        if distance < min_distance:
            min_distance = distance
            position = i

    if position >= -1 and min_distance <= max_distance:
        return position

    else:
        return None

def extract_amplified_region(left_primer, right_primer, sequence, max_distance,
        min_length, max_length):
    """Use hamming_find to locate left_primer and right_primer to extract the
    amplicon from a Fasta object's sequence
    """

    pos_left = hamming_find(left_primer, sequence, max_distance)
    pos_right = hamming_find(right_primer, sequence, max_distance)

    if pos_left != None and pos_right != None:
        if pos_right >= pos_left:
            pos_right = pos_right + len(right_primer)
            size = pos_right - pos_left

            if min_length <= size <= max_length:
                return sequence[pos_left: pos_right]

# Parse user input
try:
    input_fasta = sys.argv[1]
    left_primer = sys.argv[2]
    right_primer = sys.argv[3]
    max_distance = int(sys.argv[4])
    min_length = int(sys.argv[5])
    max_length = int(sys.argv[6])
    output_fasta = sys.argv[7]
except:
    print(__doc__)
    sys.exit(1)

sequences = fasta_iterator(input_fasta)

with myopen(output_fasta, "wt") as outfile:
    for seq in sequences:
        amplicon = Fasta(seq.name,
                extract_amplified_region(left_primer,
                    right_primer,
                    seq.sequence,
                    max_distance,
                    min_length,
                    max_length))
        if amplicon.sequence:
            print("Amplicon found for {} len: {}".format(seq.name, len(amplicon.sequence)))
            amplicon.write_to_file(outfile)
            outfile.flush()
        #else:
        #    print("Amplicon not found for {}".format(seq.name))
            #if len(seq.sequence) <= 1000:
            #    print("  Sequence is short enough, keeping nonetheless")
            #    seq.write_to_file(outfile)
