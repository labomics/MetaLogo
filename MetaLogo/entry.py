#!/usr/bin/env python
import sys
import os
import argparse

from .logo import LogoGroup
from .utils import read_file
from .colors import get_color_scheme
from .version import __version__
import matplotlib.pyplot as plt
import json
import uuid
import toml

def run_from_args(args):
    print('args: ', args)
    print('-----------------')
    print(f'uid: {args.uid}')

    os.makedirs(args.output_dir,exist_ok=True)
    os.makedirs(args.fa_output_dir,exist_ok=True)

    if args.color_scheme_json_file is not None:
        with open(args.color_scheme_json_file) as jsinf:
            color_scheme = json.load(jsinf)
    elif args.color_scheme_json_str is not None:
        color_scheme = json.loads(args.color_scheme_json_str)
    else:
        color_scheme = get_color_scheme(args.color_scheme)

    logogroup = LogoGroup(seqs=None, group_order = args.group_order, logo_type = args.type, group_strategy = args.group_strategy,
                          min_length = args.min_length, max_length = args.max_length, seq_file_type=args.seq_file_type,
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
                          display_range_left=args.display_range_left, display_range_right=args.display_range_right,
                          gap_score = args.gap_score,
                          padding_align = args.padding_align,
                          hide_version_tag=args.hide_version_tag,
                          sequence_type = args.sequence_type,
                          height_algorithm=args.height_algorithm,
                          seq_file=args.seq_file, output_dir=args.output_dir,fa_output_dir=args.fa_output_dir,uid=args.uid,
                          group_resolution=args.group_resolution,clustering_method=args.clustering_method,
                          clustalo_bin=args.clustalo_bin,fasttreemp_bin=args.fasttreemp_bin,fasttree_bin=args.fasttree_bin,treecluster_bin=args.treecluster_bin,
                          withtree=args.withtree, group_limit = args.group_limit,
                          auto_size=args.auto_size
                          )
    if hasattr(logogroup,'error'):
        print('error:',logogroup.error)
        return {'error':logogroup.error}
    

    logogroup.draw()
    logogroup.savefig(f'{args.output_dir}/{args.output_name}')
    print(f'{args.output_dir}/{args.output_name}',' saved')
    base_name = '.'.join(args.output_name.split('.')[:-1]) 
    if not args.output_name.endswith('.png'):
        logogroup.savefig(f'{args.output_dir}/{base_name}.png')
        print(f'{args.output_dir}/{base_name}.png', ' saved')

    if args.analysis:

        fig = logogroup.get_grp_counts_figure()
        if fig:
            fig = fig.figure
            count_name = f'{args.output_dir}/{base_name}.counts.png'
            fig.savefig(count_name,bbox_inches='tight')
            plt.close(fig)

        fig = logogroup.get_seq_lengths_dist()
        if fig:
            fig = fig.figure
            lengths_name = f'{args.output_dir}/{base_name}.lengths.png'
            fig.savefig(lengths_name,bbox_inches='tight')
            plt.close(fig)


        fig = logogroup.get_entropy_figure()
        if fig:
            entropy_name = f'{args.output_dir}/{base_name}.entropy.png'
            fig.savefig(entropy_name,bbox_inches='tight')
            plt.close(fig)

        boxplot_entropy_name = f'{args.output_dir}/{base_name}.boxplot_entropy.png'
        fig = logogroup.get_boxplot_entropy_figure()
        if fig:
            fig = fig.figure
            fig.savefig(boxplot_entropy_name,bbox_inches='tight')
            plt.close(fig)

        if args.padding_align or args.group_strategy=='auto':
            clustermap_name = f'{args.output_dir}/{base_name}.clustermap.png'
            fig = logogroup.get_correlation_figure()
            if fig:
                fig.savefig(clustermap_name,bbox_inches='tight')
    
    return None
 

def run_from_config(config_file):

    config = toml.load(config_file)
    print(config)
    print('-----------------')

    uid = config['uid']
    print('uid: ', uid)

    os.makedirs(config['output_dir'],exist_ok=True)
    os.makedirs(config['fa_output_dir'],exist_ok=True)

    logogroup = LogoGroup(seqs=None, **config)

    if hasattr(logogroup,'error'):
        print('error:',logogroup.error)
        return {'error':logogroup.error}

    logogroup.draw()

    logogroup.savefig(f"{config['output_dir']}/{uid}.{config['logo_format']}")
    print(f"{config['output_dir']}/{uid}.{config['logo_format']}",' saved')

    if  config['logo_format'].lower() != 'png':
        logogroup.savefig(f"{config['output_dir']}/{uid}.png")
        print(f"{config['output_dir']}/{uid}.png', ' saved")
    
    

    if config['analysis']:
        format = 'png'
        if 'analysis_format' in config:
            format = config['analysis_format']

        fig = logogroup.get_grp_counts_figure()
        if fig:
            fig =fig.figure
            count_name = f"{config['output_dir']}/{uid}.counts.png"
            fig.savefig(count_name,bbox_inches='tight')
            if format != 'png':
                count_name = f"{config['output_dir']}/{uid}.counts.{format}"
                fig.savefig(count_name,bbox_inches='tight')
            plt.close(fig)

        fig = logogroup.get_seq_lengths_dist()
        if fig:
            fig = fig.figure
            lengths_name = f"{config['output_dir']}/{uid}.lengths.png"
            fig.savefig(lengths_name,bbox_inches='tight')
            if format != 'png':
                lengths_name = f"{config['output_dir']}/{uid}.lengths.{format}"
                fig.savefig(lengths_name,bbox_inches='tight')
            plt.close(fig)


        fig = logogroup.get_entropy_figure()
        if fig:
            entropy_name = f"{config['output_dir']}/{uid}.entropy.png"
            fig.savefig(entropy_name,bbox_inches='tight')
            if format != 'png':
                entropy_name = f"{config['output_dir']}/{uid}.entropy.{format}"
                fig.savefig(entropy_name,bbox_inches='tight')
            plt.close(fig)

        fig = logogroup.get_boxplot_entropy_figure()
        if fig:
            fig =fig.figure
            boxplot_entropy_name = f"{config['output_dir']}/{uid}.boxplot_entropy.png"
            fig.savefig(boxplot_entropy_name,bbox_inches='tight')
            if format != 'png':
                boxplot_entropy_name = f"{config['output_dir']}/{uid}.boxplot_entropy.{format}"
                fig.savefig(boxplot_entropy_name,bbox_inches='tight')

            plt.close(fig)

        if config.get('padding_align',False) or config.get('group_strategy','')=='auto':
            clustermap_name = f"{config['output_dir']}/{uid}.clustermap.png"
            fig = logogroup.get_correlation_figure()
            if fig:
                fig.savefig(clustermap_name,bbox_inches='tight')
                if format != 'png':
                    clustermap_name = f"{config['output_dir']}/{uid}.clustermap.{format}"
                    fig.savefig(clustermap_name,bbox_inches='tight')
    
    return None




def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--config',type=str,help='The config file contain sequences',default=None)

    parser.add_argument('--type',type=str,help='Choose the layout type of sequence logo',choices=['Horizontal','Circle','Radiation','Threed'],default='Horizontal')
    parser.add_argument('--seq_file',type=str,help='The input file contain sequences')
    parser.add_argument('--seq_file_type',type=str,help='The type of input file', choices=['fasta','fastq'],default='fasta')
    parser.add_argument('--sequence_type',type=str,help='The type of sequences',choices=['auto','dna','rna','aa'],default='auto')

    #task
    parser.add_argument('--task_name',type=str,help='The title to displayed on the figure',default='MetaLogo')
    
    #sequences
    parser.add_argument('--min_length',type=int,help='The minimum length of sequences to be included',default=8)
    parser.add_argument('--max_length',type=int,help='The maximum length of sequences to be included',default=20)

    #group
    parser.add_argument('--group_strategy',type=str,help='The strategy to separate sequences into groups',choices=['auto','length','identifier'],default='auto')
    parser.add_argument('--clustering_method',type=str,help='The method for tree clustering',default='max')
    parser.add_argument('--group_resolution',type=float,help='The resolution for sequence grouping',default=0.5)
    parser.add_argument('--group_limit',type=int,help='The limit for group number',default=20)

    #sort
    parser.add_argument('--group_order',type=str,help='The order of groups',choices=['length','length_reverse','identifier','identifier_reverse'],default='length')

    #color
    parser.add_argument('--color_scheme',type=str,help='The color scheme',choices=['basic_dna_color','basic_rna_color','basic_aa_color'],default='basic_dna_color')
    parser.add_argument('--color_scheme_json_str',type=str,help='The json string of color scheme',default=None)
    parser.add_argument('--color_scheme_json_file',type=str,help='The json file of color scheme',default=None)

    #align
    parser.add_argument('--height_algorithm',type=str,help='The algorithm for character height',default='bits',choices=['bits','bits_without_correction','probabilities'])

    parser.add_argument('--align',action='store_true',dest='align', help='If show alignment of adjacent sequence logo')
    parser.add_argument('--padding_align',action='store_true',dest='padding_align', help='If padding logos to make multiple logo alignment')

    parser.add_argument('--align_metric',type=str,help='The metric for align score',default='dot_product',choices=['dot_product','js_divergence','cosine','entropy_bhattacharyya'])
    parser.add_argument('--connect_threshold',type=float,help='The align threshold',default=0.8)

    parser.add_argument('--gap_score',type=float,help='The gap score for alignment',default=-1.0)

    #display range
    parser.add_argument('--display_range_left',type=int,help='The start position of display range (Global alignment with padding required)',default=0)
    parser.add_argument('--display_range_right',type=int,help='Then end position of display range (Global alignment with padding requirement)',default=-1)

    #layout
    parser.add_argument('--withtree',action='store_true',dest='withtree', help='If show tree besides sequence logo')

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

    parser.add_argument('--figure_size_x',type=float,help='The width of figure',default=20)
    parser.add_argument('--figure_size_y',type=float,help='The height of figure',default=10)
    parser.add_argument('--auto_size',action='store_true',dest='auto_size',help='Let MetaLogo determine the size of figures')

    parser.add_argument('--align_color',type=str,help='The color of alignment',default='blue')
    parser.add_argument('--align_alpha',type=float,help='The transparency of alignment',default='0.2')

    #output 
    parser.add_argument('--output_dir',type=str,help='Output path of figure',default='figure_output')
    parser.add_argument('--output_name',type=str,help='Output name of figure',default='test.png')
    parser.add_argument('--fa_output_dir',type=str,help='Output path of fas',default='sequence_input')
    parser.add_argument('--uid',type=str,help='Task id',default=str(uuid.uuid4()))

    parser.add_argument('--logo_format',type=str,help='The format of figures',choices=['png','pdf'],default='png')

    #analysis
    parser.add_argument('--analysis',action='store_true',dest='analysis',help='If perform basic analysis on data')

    #software
    parser.add_argument('--clustalo_bin',type=str,help='The path of clustalo bin ',default='/usr/bin/clustalo')
    parser.add_argument('--fasttree_bin',type=str,help='The path of fasttree bin ',default='/usr/bin/FastTree')
    parser.add_argument('--fasttreemp_bin',type=str,help='The path of fasttreeMP bin ',default='/usr/bin/FastTreeMP')
    parser.add_argument('--treecluster_bin',type=str,help='The path of treecluster bin ',default='TreeCluster.py')

    parser.add_argument('-v', '--version', action='version', version=__version__)

    args = parser.parse_args()


    if args.config is not None:
        run_from_config(args.config)
    else:
        run_from_args(args)


if __name__ == '__main__':
    main()