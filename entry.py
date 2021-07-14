#!/usr/bin/python
import argparse

from logo import LogoGroup
from utils import read_file
from utils import grouping
from utils import compute_bits


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--type',type=str,help='Choose the type of sequence logo',default='Horizontal')
    parser.add_argument('--input_file',type=str,help='The input file contain sequences',default='test.fa')
    parser.add_argument('--input_file_type',type=str,help='The type of input file',default='fasta')

    
    #sequences
    parser.add_argument('--min_length',type=int,help='The minimum length of sequences to be included',default=25)
    parser.add_argument('--max_length',type=int,help='The maximum length of sequences to be included',default=27)

    #tmp
    parser.add_argument('--tmp_path',type=str,help='The location to store tmp files',default='tmp/')

    #group
    parser.add_argument('--group_strategy',type=str,help='The strategy to seperate sequences into groups',default='by_length')
    parser.add_argument('--group_info',type=str,help='The file contains group information of sequences')
    parser.add_argument('--group_limit',type=str,help='The number of groups to be showed on the figure',default=5)
    parser.add_argument('--select_group',type=str,help='How to choose the groups, by options: most_seqnum, least_seqnum, longest, shortest, first, last, random',default='most_seqnum')

    #sort
    parser.add_argument('--group_order',type=str,help='The order of groups',default='length')

    #color
    parser.add_argument('--color_scheme',type=str,help='The color scheme')
    parser.add_argument('--color_file',type=str,help='The file specify the color scheme')

    #font
    parser.add_argument('--font',type=str,help='The font of sequence characters')

    #align
    parser.add_argument('--align',type=bool,help='If show alignment of different sequence logo')
    parser.add_argument('--align_type',type=str,help='The align type between different sequence logos',default='normal')

    #style
    parser.add_argument('--hide_X',type=bool,help='If hide X axis')
    parser.add_argument('--hide_X_ticks',type=bool,help='If hide ticks of X axis')
    parser.add_argument('--hide_Y',type=bool,help='If hide X axis')
    parser.add_argument('--hide_Y_ticks',type=bool,help='If hide ticks of Y axis')
    parser.add_argument('--X_label',type=bool,help='The label for X axis')
    parser.add_argument('--Y_label',type=bool,help='The label for Y axis')

    #output 
    parser.add_argument('--show_X',type=bool,help='If show alignment of different sequence logo')
    args = parser.parse_args()

    #read seqs
    #print(args.input_file)
    seqs = read_file(args.input_file, args.input_file_type, args.min_length, args.max_length)
    #group seqs
    #print(seqs)

    groups = grouping(seqs,group_by='length')
    bits = compute_bits(groups,args.tmp_path)
    #print(groups)

    logogroup = LogoGroup(bits,args.group_order)
    print(logogroup.logos)
    logogroup.savefig()

