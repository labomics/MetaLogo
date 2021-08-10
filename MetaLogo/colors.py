#!/usr/bin/env python

basic_dna_color_scheme = {'A': '#009980',
        'C': '#59B3E6',
        'G': '#E69B04',
        'T': '#1A1A1A',
        '-': 'grey'}

basic_rna_color_scheme = {'A': '#009980',
        'C': '#59B3E6',
        'G': '#E69B04',
        'U': '#1A1A1A',
        '-': 'grey'}


basic_aa_color_scheme ={ #https://jbloomlab.github.io/dmslogo/dmslogo.colorschemes.html
        'A': 'black',
        'C': 'green',
        'D': 'red',
        'E': 'red',
        'F': 'black',
        'G': 'green',
        'H': 'blue',
        'I': 'black',
        'K': 'blue',
        'L': 'black',
        'M': 'black',
        'N': '#FF00AE',
        'P': 'black',
        'Q': '#FF00AE',
        'R': 'blue',
        'S': 'green',
        'T': 'green',
        'V': 'black',
        'W': 'black',
        'Y': 'green'
    }
 
def get_color_scheme(scheme):
    if scheme == 'basic_dna_color':
        return basic_dna_color_scheme
    if scheme == 'basic_rna_color':
        return basic_rna_color_scheme
    if scheme == 'basic_aa_color':
        return basic_aa_color_scheme
    return None
