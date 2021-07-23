#!/usr/bin/python
import argparse

from .logo import LogoGroup
from .utils import read_file
from .utils import grouping,check_group
from .utils import compute_bits


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--type',type=str,help='Choose the type of sequence logo',default='Horizontal')
    #parser.add_argument('--input_file',type=str,help='The input file contain sequences',default='test/test.fa')
    parser.add_argument('--input_file',type=str,help='The input file contain sequences',default='vllogo/dash/examples/bug.fa')
    parser.add_argument('--input_file_type',type=str,help='The type of input file',default='fasta')
    parser.add_argument('--sequence_type',type=str,help='The type of sequences',default='dna')

    
    #sequences
    parser.add_argument('--min_length',type=int,help='The minimum length of sequences to be included',default=8)
    parser.add_argument('--max_length',type=int,help='The maximum length of sequences to be included',default=20)

    #tmp
    parser.add_argument('--tmp_path',type=str,help='The location to store tmp files',default='tmp/')

    #group
    parser.add_argument('--group_strategy',type=str,help='The strategy to seperate sequences into groups',default='length')
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
    parser.add_argument('--align',action='store_true',dest='align', help='If show alignment of different sequence logo')

    parser.add_argument('--align_metric',type=str,help='The metric for align score',default='sort_consistency')
    parser.add_argument('--align_threshold',type=float,help='The align threshold',default=0.8)

    #style
    parser.add_argument('--hide_X',action='store_true',dest='hide_X',help='If hide X axis')
    parser.add_argument('--hide_X_ticks',action='store_true',dest='hide_X_ticks',help='If hide ticks of X axis')
    parser.add_argument('--hide_Y',action='store_true',dest='hide_Y',help='If hide Y axis')
    parser.add_argument('--hide_Y_ticks',action='store_true',dest='hide_Y_ticks',help='If hide ticks of Y axis')
    parser.add_argument('--X_label', action='store_true',dest='X_label', help='The label for X axis')
    parser.add_argument('--Y_label', action='store_true',dest='Y_label', help='The label for Y axis')

    #output 
    parser.add_argument('--output_dir',type=str,help='Output name of figure',default='test')
    parser.add_argument('--output_name',type=str,help='Output name of figure',default='test.png')
    
    #parser.set_defaults(align=True)
    args = parser.parse_args()

    print('args: ',args)
    #read seqs
    print(args.input_file)
    seqs = read_file(args.input_file, args.input_file_type, args.min_length, args.max_length)
    #print('seqs:', seqs)
    #if len(seqs) == 0:
    #    print('no sequences detected')
    #group seqs
    #print(args.input_file, args.input_file_type, args.min_length, args.max_length,seqs)
    #print('logotype:',args.type)

    groups = grouping(seqs,group_by=args.group_strategy)
    check_group(groups)
    #print('groups:', groups)
    print('in entry: seq_type: ',args.sequence_type)
    bits = compute_bits(groups,args.tmp_path,seq_type=args.sequence_type)

    #print('bits: ',bits)
    #print(groups)
    #print('align: ',args.align)

    logogroup = LogoGroup(bits, args.group_order, logo_type = args.type, align=args.align, align_metric=args.align_metric, align_threshold = args.align_threshold)
    logogroup.draw()
    logogroup.savefig(f'{args.output_dir}/{args.output_name}')
    if not args.output_name.endswith('.png'):
        base = '.'.join(args.output_name.split('.')[:-1]) 
        logogroup.savefig(f'{args.output_dir}/{base}.png')
    


