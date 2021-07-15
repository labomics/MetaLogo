#!/usr/bin/python

basic_dna_color_map = {'A': '#009980',
        'C': '#59B3E6',
        'G': '#E69B04',
        'T': '#1A1A1A',
        'other': 'grey'}

def get_color_scheme(scheme):
    if scheme == 'basic_dna_color':
        return basic_dna_color_map