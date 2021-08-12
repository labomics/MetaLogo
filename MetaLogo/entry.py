#!/usr/bin/env python
import argparse

from .logo import LogoGroup
from .utils import read_file
from .colors import get_color_scheme
from .version import __version__
import json



def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--type',type=str,help='Choose the layout type of sequence logo',choices=['Horizontal','Circle','Radiation','Threed'],default='Horizontal')
    parser.add_argument('--input_file',type=str,help='The input file contain sequences',required=True)
    parser.add_argument('--input_file_type',type=str,help='The type of input file', choices=['fasta','fastq'],default='fasta')
    parser.add_argument('--sequence_type',type=str,help='The type of sequences',choices=['auto','dna','rna','aa'],default='auto')

    #task
    parser.add_argument('--task_name',type=str,help='The title to displayed on the figure',default='MetaLogo')
    
    #sequences
    parser.add_argument('--min_length',type=int,help='The minimum length of sequences to be included',default=8)
    parser.add_argument('--max_length',type=int,help='The maximum length of sequences to be included',default=20)

    #group
    parser.add_argument('--group_strategy',type=str,help='The strategy to separate sequences into groups',choices=['length','identifier'],default='length')

    #sort
    parser.add_argument('--group_order',type=str,help='The order of groups',choices=['length','length_reverse','identifier','identifier_reverse'],default='length')

    #color
    parser.add_argument('--color_scheme',type=str,help='The color scheme',choices=['basic_dna_color','basic_rna_color','basic_aa_color'],default='basic_dna_color')
    parser.add_argument('--color_scheme_json',type=str,help='The json file of color scheme',default=None)

    #align
    parser.add_argument('--height_algorithm',type=str,help='The algorithm for character height',default='bits',choices=['bits','probabilities'])

    parser.add_argument('--align',action='store_true',dest='align', help='If show alignment of adjacent sequence logo')
    parser.add_argument('--padding_align',action='store_true',dest='padding_align', help='If padding logos to make multiple logo alignment')

    parser.add_argument('--align_metric',type=str,help='The metric for align score',default='dot_product',choices=['dot_product','js_divergence','cosine','entropy_bhattacharyya'])
    parser.add_argument('--connect_threshold',type=float,help='The align threshold',default=0.8)

    parser.add_argument('--gap_score',type=float,help='The gap score for alignment',default=-1.0)

    #layout

    parser.add_argument('--logo_margin_ratio',type=float,help='Margin ratio between the logos',default=0.1)
    parser.add_argument('--column_margin_ratio',type=float,help='Margin ratio between the columns',default=0.05)
    parser.add_argument('--char_margin_ratio',type=float,help='Margin ratio between the chars',default=0.05)

    #style

    parser.add_argument('--hide_version_tag',action='store_true',dest='hide_version_tag',help='If show version tag of MetaLogo')

    parser.add_argument('--hide_left_axis',action='store_true',dest='hide_left_axis',help='If hide left axis')
    parser.add_argument('--hide_right_axis',action='store_true',dest='hide_right_axis',help='If hide right axis')
    parser.add_argument('--hide_top_axis',action='store_true',dest='hide_top_axis',help='If hide top axis')
    parser.add_argument('--hide_bottom_axis',action='store_true',dest='hide_bottom_axis',help='If hide bottom axis')

    parser.add_argument('--hide_x_ticks',action='store_true',dest='hide_x_ticks',help='If hide ticks of X axis')
    parser.add_argument('--hide_y_ticks',action='store_true',dest='hide_y_ticks',help='If hide ticks of Y axis')
    parser.add_argument('--hide_z_ticks',action='store_true',dest='hide_z_ticks',help='If hide ticks of Z axis')

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

    parser.add_argument('--align_color',type=str,help='The color of alignment',default='blue')
    parser.add_argument('--align_alpha',type=float,help='The transparency of alignment',default='0.2')

    #output 
    parser.add_argument('--output_dir',type=str,help='Output path of figure',default='.')
    parser.add_argument('--output_name',type=str,help='Output name of figure',default='test.png')

    parser.add_argument('-v', '--version', action='version', version=__version__)

    
    args = parser.parse_args()
    print('args: ', args)

    seqs = read_file(args.input_file, args.input_file_type, args.min_length, args.max_length)

    if args.color_scheme_json is not None:
        with open(args.color_scheme_json) as jsinf:
            color_scheme = json.load(jsinf)
    else:
        color_scheme = get_color_scheme(args.color_scheme)
    

    logogroup = LogoGroup(seqs, group_order = args.group_order, logo_type = args.type, group_strategy = args.group_strategy,
                          align=args.align, align_metric=args.align_metric, connect_threshold = args.connect_threshold,
                          color=color_scheme, task_name=args.task_name, hide_left_axis = args.hide_left_axis,
                          hide_right_axis = args.hide_right_axis, hide_bottom_axis = args.hide_bottom_axis,
                          hide_top_axis = args.hide_top_axis, show_grid = args.show_grid, show_group_id = args.show_group_id,
                          hide_x_ticks = args.hide_x_ticks, hide_y_ticks = args.hide_y_ticks, hide_z_ticks=args.hide_z_ticks,
                          x_label=args.x_label, y_label=args.y_label, z_label=args.z_label,
                          title_size=args.title_size, label_size=args.label_size, group_id_size=args.group_id_size,
                          tick_size=args.tick_size, logo_margin_ratio = args.logo_margin_ratio, column_margin_ratio = args.column_margin_ratio,
                          figure_size_x=args.figure_size_x, figure_size_y=args.figure_size_y,
                          char_margin_ratio = args.char_margin_ratio, align_color=args.align_color,align_alpha=args.align_alpha ,
                          gap_score = args.gap_score,
                          padding_align = args.padding_align,
                          hide_version_tag=args.hide_version_tag,
                          sequence_type = args.sequence_type,
                          height_algorithm=args.height_algorithm
                          )
    logogroup.draw()
    logogroup.savefig(f'{args.output_dir}/{args.output_name}')
    print(f'{args.output_dir}/{args.output_name}',' saved')
    if not args.output_name.endswith('.png'):
        base = '.'.join(args.output_name.split('.')[:-1]) 
        logogroup.savefig(f'{args.output_dir}/{base}.png')
        print(f'{args.output_dir}/{base}.png', ' saved')
    

if __name__ == '__main__':
    main()