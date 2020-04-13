#! /usr/bin/env python3

import sys
import re

def vet_nucleotide_sequence(sequence):
    rna_pattern_str = r'^[AUCGaucg]*$'
    dna_pattern_str = r'^[ATCGatcg]*$'

    rna_pattern = re.compile(rna_pattern_str)
    dna_pattern = re.compile(dna_pattern_str)

    if rna_pattern.match(sequence):
        return
    if dna_pattern.match(sequence):
        return
    else:
        raise Exception("Invalid sequence: {0!r}".format(sequence))


def vet_codon(codon):
    codon_pattern_str = r'^[AUGCaucg]{3}$'
    codon_pattern = re.compile(codon_pattern_str)

    if codon_pattern.match(codon):
        return
    else:
        raise Exception("Invalid codon: {0!r}".format(codon))


def find_first_orf(sequence,
        start_codons = ['AUG'],
        stop_codons = ['UAA', 'UAG', 'UGA']):

    # Make sure the sequence is valid
    vet_nucleotide_sequence(sequence)

    # Make sure the codons are valid
    for codon in start_codons:
        vet_codon(codon)
    for codon in stop_codons:
        vet_codon(codon)

    # Get copies of everything in uppercase
    seq = sequence.upper()
    starts = [c.upper() for c in start_codons]
    stops = [c.upper() for c in stop_codons]

    # Make sure seq is RNA
    seq = seq.replace('T', 'U')

    # Hardicoding start and stop codons:
    stac = '|'.join(start_codons)
    stoc = '|'.join(stop_codons)
    orf_pattern_str = r'('+stac+r')([AUCG]{3})*('+stoc+r')'

    # Create the regular expression object
    orf_pattern = re.compile(orf_pattern_str)

    # Search the sequence
    match_object = orf_pattern.search(seq)
    if match_object:
        return match_object.group()
    return ''


def parse_sequence_from_path(path):
    # Try to open the path to read from it, and handle exceptions if they
    # arise
    try:
        file_stream = open(path, 'r')
    except FileNotFoundError as e:
        sys.stderr.write("Sorry, couldn't find path {}".format(path))
        raise e
    except IsADirectoryError as e:
        sys.stderr.write("Sorry, path {} appears to be a directory".format(path))
        raise e
    except:
        sys.stderr.write("Sorry, something went wrong when trying to open {}".format(path))
        raise
    # If we've reached here, the file is open and ready to read
    sequence = ''
    # A for loop to visit each line in the file
    for line in file_stream:
        # Strip whitespace from the line and concatenate it to the end of the
        # sequence
        sequence += line.strip()
    return sequence


def main():
    import argparse

    # Create a command-line parser object
    parser = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    # Tell the parser what command-line arguments this script can receive
    parser.add_argument('sequence',
            metavar = 'SEQUENCE',
            type = str,
            help = ('The sequence to search for an open-reading frame. '
                    'If the path flag (\'-p\'/\'--path\') is specified, '
                    'then this should be a path to a file containing the '
                    'sequence to be searched.'))
    parser.add_argument('-p', '--path',
            action = 'store_true',
            help = ('The sequence argument should be treated as a path to a '
                    'containing the sequence to be searched.'))
    parser.add_argument('-s', '--start-codons',
            type = str,
            nargs = '+', # one or more arguments
            default = ['AUG'],
            help = ('One or more possible start codons.'))
    parser.add_argument('-x', '--stop-codons',
            type = str,
            nargs = '+', # one or more arguments
            default = ['UAA', 'UAG', 'UGA'],
            help = ('One or more possible stop codons.'))

    # Parse the command-line arguments into a 'dict'-like container
    args = parser.parse_args()

    # Check to see if the path option was set to True by the caller. If so, parse
    # the sequence from the path
    if args.path:
        sequence = parse_sequence_from_path(args.sequence)
    else:
        sequence = args.sequence

    orf = find_first_orf(sequence = sequence,
            start_codons = args.start_codons,
            stop_codons = args.stop_codons)
    sys.stdout.write('{}\n'.format(orf))

if __name__ == '__main__':
    main()
