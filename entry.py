#!/usr/bin/python
import argparse

from .logo import LogoGroup
from .utils import read_file
from .utils import grouping,check_group
from .utils import compute_bits
from .colors import get_color_scheme
import json
import os


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--type',type=str,help='Choose the type of sequence logo',default='Horizontal')
    parser.add_argument('--input_file',type=str,help='The input file contain sequences',default='test/test.fa')
    #parser.add_argument('--input_file',type=str,help='The input file contain sequences',default='vllogo/dash/examples/bug.fa')
    parser.add_argument('--input_file_type',type=str,help='The type of input file',default='fasta')
    parser.add_argument('--sequence_type',type=str,help='The type of sequences',default='dna')

    #task
    parser.add_argument('--task_name',type=str,help='The name to displayed on the figure',default='MetaLogo')
    
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

    #layout

    parser.add_argument('--logo_margin_ratio',type=float,help='Margin ratio between the logos',default=0.1)
    parser.add_argument('--column_margin_ratio',type=float,help='Margin ratio between the columns',default=0.05)
    parser.add_argument('--char_margin_ratio',type=float,help='Margin ratio between the chars',default=0.05)

    #style

    parser.add_argument('--hide_left_axis',action='store_true',dest='hide_left_axis',help='If show left axis')
    parser.add_argument('--hide_right_axis',action='store_true',dest='hide_right_axis',help='If show right axis')
    parser.add_argument('--hide_top_axis',action='store_true',dest='hide_top_axis',help='If show top axis')
    parser.add_argument('--hide_bottom_axis',action='store_true',dest='hide_bottom_axis',help='If show bottom axis')

    parser.add_argument('--hide_x_ticks',action='store_true',dest='hide_x_ticks',help='If show ticks of X axis')
    parser.add_argument('--hide_y_ticks',action='store_true',dest='hide_y_ticks',help='If show ticks of Y axis')
    parser.add_argument('--hide_z_ticks',action='store_true',dest='hide_z_ticks',help='If show ticks of Z axis')

    parser.add_argument('--x_label', type=str, help='The label for X axis')
    parser.add_argument('--y_label', type=str, help='The label for Y axis')
    parser.add_argument('--z_label', type=str, help='The label for Z axis')

    parser.add_argument('--show_group_id',action='store_true',dest='show_group_id',help='If show group ids')
    parser.add_argument('--show_grid',action='store_true',dest='show_grid',help='If show background grid')


    parser.add_argument('--title_size',type=int,help='The size of figure title',default=20)
    parser.add_argument('--label_size',type=int,help='The size of figure xy labels',default=10)
    parser.add_argument('--tick_size',type=int,help='The size of figure ticks',default=10)
    parser.add_argument('--group_id_size',type=int,help='The size of group labels',default=10)

    parser.add_argument('--figure_size_x',type=float,help='The width of figure',default=10)
    parser.add_argument('--figure_size_y',type=float,help='The height of figure',default=10)

    parser.add_argument('--align_color',type=str,help='The color of alignment',default=10)
    parser.add_argument('--align_alpha',type=float,help='The transparency of alignment',default=10)

    #output 
    parser.add_argument('--output_dir',type=str,help='Output name of figure',default='test')
    parser.add_argument('--output_name',type=str,help='Output name of figure',default='test.png')
    
    args = parser.parse_args()
    print('args: ', args)

    seqs = read_file(args.input_file, args.input_file_type, args.min_length, args.max_length)

    groups = grouping(seqs,group_by=args.group_strategy)
    check_group(groups)
    bits = compute_bits(groups,args.tmp_path,seq_type=args.sequence_type)

    print('args.color_scheme: ', args.color_scheme)
    #get color
    try:
        color_scheme = get_color_scheme(args.color_scheme)
        if color_scheme is None:
            parsed_scheme = json.loads(args.color_scheme)
            if type(parsed_scheme) ==  type({}):
                color_scheme = parsed_scheme
            else:
                color_scheme = get_color_scheme('basic_aa_color')
    except Exception as e:
        color_scheme = get_color_scheme('basic_aa_color')
    
    print('color_scheme: ', color_scheme)

    logogroup = LogoGroup(bits, args.group_order, logo_type = args.type, 
                          align=args.align, align_metric=args.align_metric, align_threshold = args.align_threshold,
                          color=color_scheme, task_name=args.task_name, hide_left_axis = args.hide_left_axis,
                          hide_right_axis = args.hide_right_axis, hide_bottom_axis = args.hide_bottom_axis,
                          hide_top_axis = args.hide_top_axis, show_grid = args.show_grid, show_group_id = args.show_group_id,
                          hide_x_ticks = args.hide_x_ticks, hide_y_ticks = args.hide_y_ticks, hide_z_ticks=args.hide_z_ticks,
                          x_label=args.x_label, y_label=args.y_label, z_label=args.z_label,
                          title_size=args.title_size, label_size=args.label_size, group_id_size=args.group_id_size,
                          tick_size=args.tick_size, logo_margin_ratio = args.logo_margin_ratio, column_margin_ratio = args.column_margin_ratio,
                          figure_size_x=args.figure_size_x, figure_size_y=args.figure_size_y,
                          char_margin_ratio = args.char_margin_ratio, align_color=args.align_color,align_alpha=args.align_alpha 
                          )
    logogroup.draw()
    logogroup.savefig(f'{args.output_dir}/{args.output_name}')
    if not args.output_name.endswith('.png'):
        base = '.'.join(args.output_name.split('.')[:-1]) 
        logogroup.savefig(f'{args.output_dir}/{base}.png')
    

