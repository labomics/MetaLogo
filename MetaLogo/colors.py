#!/usr/bin/python

basic_dna_color_map = {'A': '#009980',
        'C': '#59B3E6',
        'G': '#E69B04',
        'T': '#1A1A1A',
        'other': 'grey'}

aa_color_map = {
    "A":"#CCFF00",
    "C":"#FFFF00",
    "D":"#FF0000",
    "E":"#FF0066",
    "F":"#00FF66",
    "G":"#FF9900",
    "H":"#0066FF",
    "I":"#66FF00",
    "K":"#6600FF",
    "L":"#33FF00",
    "M":"#00FF00",
    "N":"#CC00FF",
    "P":"#FFCC00",
    "Q":"#FF00CC",
    "R":"#0000FF",
    "S":"#FF3300",
    "T":"#FF6600",
    "V":"#99FF00",
    "W":"#00CCFF",
    "Y":"#00FFCC"
}

def get_color_scheme(scheme):
    if scheme == 'basic_dna_color':
        return basic_dna_color_map
    if scheme == 'basic_aa_color':
        return aa_color_map
    return None
