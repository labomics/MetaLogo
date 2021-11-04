#!/usr/bin/env python
import genericpath
from typing import Sequence
from matplotlib import transforms
from matplotlib.colors import get_named_colors_mapping
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, get
import numpy as np
from matplotlib.patches import Circle
from .character import Character
from .column import Column
from .item import Item
from .utils import get_coor_by_angle,  link_edges, rotate, text3d
from .connect import get_connect, get_score_mat, msa
from matplotlib.patches import Circle, PathPatch
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
import mpl_toolkits.mplot3d.art3d as art3d
import seaborn as sns
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, RegularPolygon
from numpy import radians as rad
import math
import re
import time
import pandas as pd
import pathlib
import os

from .utils import grouping,check_group,detect_seq_type
from .logobits import compute_bits, compute_prob
from .colors import get_color_scheme
from .version import __version__

basic_dna_color = get_color_scheme('basic_dna_color')


class Logo(Item):
    def __init__(self, bits, ax = None, start_pos=(0,0), logo_type='Horizontal', column_width=1, 
                 column_margin_ratio=0.1, char_margin_ratio = 0.1, parent_start = (0,0), origin = (0,0), id='', 
                 help_color='b', color=basic_dna_color, limited_char_width=None, path_dict={}, *args, **kwargs):
        super(Logo, self).__init__(*args, **kwargs)

        self.bits = bits
        self.start_pos = start_pos
        self.logo_type = logo_type
        self.parent_start = parent_start
        self.column_margin_ratio = column_margin_ratio
        self.char_margin_ratio = char_margin_ratio
        self.column_width = column_width
        self.origin = origin
        self.id = id
        self.color = color
        self.help_color = help_color
        self.columns = []
        self.limited_char_width = limited_char_width
        self.path_dict = path_dict

        if ax == None:
            self.ax = self.generate_ax(threed=(self.logo_type=='Threed'))
        else:
            self.ax = ax

        if limited_char_width == None:
            self.limited_char_width = self.get_limited_char_width()
        
        self.generate_components()


    def generate_components(self):
        for index,bit in enumerate(self.bits):
            chars = [x[0] for x in bit]
            weights = [x[1] for x in bit]
            if chars == []:
                chars = ['-']
                weights = [0]
            column = Column(chars,weights,ax=self.ax,width=self.column_width,logo_type=self.logo_type,
                            origin=self.origin, color=self.color, char_margin_ratio=self.char_margin_ratio,
                            limited_char_width=self.limited_char_width,path_dict=self.path_dict)
            self.columns.append(column)
    
    def draw(self):
        self.compute_positions()
        for col in self.columns:
            col.draw()
    
    def draw_help(self,show_id=True,group_id_size=10, **kwargs):

        if self.logo_type == 'Threed': 
            self.draw_3d_help(show_id=show_id, group_id_size=group_id_size, **kwargs)
       
        if self.logo_type == 'Horizontal': 
            self.draw_hz_help(show_id=show_id, group_id_size=group_id_size,**kwargs)
        
        if self.logo_type == 'Circle':
            self.draw_circle_help(show_id=show_id, group_id_size=group_id_size,**kwargs)
        
        if self.logo_type == 'Radiation':
            self.draw_rad_help(show_id=show_id, group_id_size=group_id_size,**kwargs)
    
    def draw_rad_help(self, show_id=True, group_id_size=10, **kwargs):
        if show_id:
            label_radius = (self.start_pos[0] + self.get_width() ) 
            label_x = label_radius * np.cos(self.deg)
            label_y = label_radius * np.sin(self.deg)
            self.id_txt = self.ax.text(label_x,label_y, f'{self.id}',rotation=math.degrees(self.deg),fontsize=group_id_size)
    
    def draw_hz_help(self,show_id=True,group_id_size=10, **kwargs):
        if show_id:
            #self.id_txt = self.ax.text(self.get_width() + 0.5, self.start_pos[1]+0.1,
            self.id_txt = self.ax.text(self.get_width() + 0.5, self.start_pos[1]+self.get_height()*0.1,
                                     f"{self.id}", fontsize=group_id_size, clip_on=True)#,bbox={'fc': '0.8', 'pad': 0})
        

        
    def draw_circle_help(self,show_id=True, group_id_size=10,draw_arrow=False,**kwargs):
        self.ax.add_patch(Circle(self.parent_start,self.radius,linewidth=1,fill=False,edgecolor='grey',alpha=0.5))

        space_deg = self.degs[0] + (self.degs[-1] - self.degs[0])/2
        space_coor = get_coor_by_angle(self.radius ,space_deg)
        self.ax.scatter(space_coor[0],space_coor[1],color=self.help_color)

        space_coor2 = get_coor_by_angle(self.radius + self.get_height() ,space_deg)
        #self.ax.plot([self.parent_start[0],space_coor[0]],[self.parent_start[1],space_coor[1]],zorder=-1)

        self.ax.plot([space_coor[0],space_coor2[0]],[space_coor[1],space_coor2[1]],zorder=-1,color='grey')

        if draw_arrow == True:
            self.ax.plot([self.origin[0],space_coor[0]],[self.origin[1],space_coor[1]],zorder=-1,color='grey')
            arc = Arc(self.origin,self.radius,self.radius,angle=270,
                  theta1=0,theta2=180,capstyle='round',linestyle='-',lw=2,color='black')
            self.ax.add_patch(arc)
            endX = 0
            endY = -self.radius/2
            self.ax.add_patch(                    #Create triangle as arrow head
                 RegularPolygon(
                    (endX, endY),            # (x,y)
                     3,                       # number of vertices
                    self.radius/9,                # radius
                    rad(30+180),     # orientation
                    color='black'
                )
            )

    
    def draw_3d_help(self,z_height_3d=2, show_id=True, group_id_size=10,**kwargs):
        if show_id:
            self.ax.text(0, self.start_pos[2], z_height_3d, f'{self.id}', 'z',fontsize=group_id_size)



    
    def compute_positions(self):

        if self.logo_type == 'Circle':
            self.column_margin_ratio = 0
            self.radius = np.sqrt((self.start_pos[0]-self.parent_start[0])**2 + (self.start_pos[1]-self.parent_start[1])**2)
            self.each_deg = 2*np.pi / len(self.bits)
            width = 2 * self.radius * np.tan(self.each_deg/2)
            width = width * 0.95
            self.column_width = width
            degs = [x*self.each_deg + np.pi/2  for x in range(len(self.bits))]
            degs = degs[::-1]
            degs = [degs.pop()] + degs
            self.degs = degs

        start_pos = self.start_pos
        for index,col in enumerate(self.columns):
            col.set_parent_start(self.start_pos)
            if self.logo_type == 'Horizontal':
                col.set_start_pos(start_pos)
                col.compute_positions()
                start_pos = (start_pos[0] + col.get_width() * (1+self.column_margin_ratio), start_pos[1])
            elif self.logo_type == 'Circle':
                start_pos = get_coor_by_angle(self.radius, self.degs[index], self.parent_start)
                col.set_start_pos(start_pos)
                col.set_deg(self.degs[index])
                col.set_width(self.column_width)
                col.compute_positions()
            elif self.logo_type == 'Radiation':
                col.set_start_pos(start_pos)
                col.set_deg(self.deg)
                col.set_radiation_space(self.radiation_space)
                col.compute_positions()
                start_pos = (start_pos[0] + col.get_width() *(1+self.column_margin_ratio), start_pos[1])
            elif self.logo_type == 'Threed':
                col.set_start_pos(start_pos)
                col.compute_positions()
                start_pos = (start_pos[0] + col.get_width() *(1+self.column_margin_ratio), start_pos[1], start_pos[2])
            else:
                pass
    
    def get_height(self):
        return max([col.get_height() for col in self.columns]+[0])
    
    def get_width(self):
        return sum([col.get_width() *(1+self.column_margin_ratio) for col in self.columns])




class LogoGroup(Item):
    def __init__(self,  seqs, ax=None, group_order='length', group_strategy='length', group_resolution=0.5, start_pos = (0,0), logo_type = 'Horizontal', init_radius=1, 
                 logo_margin_ratio = 0.1, column_margin_ratio = 0.05, char_margin_ratio = 0.05,
                 align = True, align_metric='sort_consistency', connect_threshold=0.8, 
                 radiation_head_n = 5, threed_interval = 4, color = basic_dna_color, task_name='MetaLogo',
                 x_label = 'Position', y_label = 'bits',z_label = 'bits', show_grid = True, show_group_id = True,
                 display_range_left = 0, display_range_right = -1,
                 hide_left_axis=False, hide_right_axis=False, hide_top_axis=False, hide_bottom_axis=False,
                 hide_x_ticks=False, hide_y_ticks=False, hide_z_ticks=False, 
                 title_size=20, label_size=10, tick_size=10, group_id_size=10,align_color='blue',align_alpha=0.1,
                 figure_size_x=-1, figure_size_y=-1,gap_score=-1, padding_align=False, hide_version_tag=False,
                 sequence_type = 'auto', height_algorithm = 'bits',omit_prob = 0,
                 seq_file = '', fa_output_dir = '', uid = '',
                 clustalo_bin = '',
                 *args, **kwargs):
        super(LogoGroup, self).__init__(*args, **kwargs)
        self.seqs = seqs
        self.seq_file = seq_file
        self.group_order = group_order
        self.group_strategy = group_strategy
        self.group_resolution = group_resolution
        self.start_pos = start_pos
        self.logo_margin_ratio = logo_margin_ratio
        self.column_margin_ratio = column_margin_ratio
        self.char_margin_ratio = char_margin_ratio
        self.logo_type = logo_type
        self.init_radius = init_radius
        self.radiation_head_n = 5
        self.threed_interval = threed_interval
        self.align = align 
        self.ceiling_pos = (0,1)
        self.align_metric = align_metric
        self.connect_threshold = connect_threshold
        self.color = color
        self.task_name = task_name

        self.height_algorithm = height_algorithm
        self.omit_prob = omit_prob

        self.align_color = align_color
        self.align_alpha = align_alpha

        self.padding_align = padding_align

        self.display_range_left = display_range_left
        self.display_range_right = display_range_right

        self.gap_score = gap_score

        self.hide_left_axis = hide_left_axis
        self.hide_right_axis = hide_right_axis
        self.hide_bottom_axis = hide_bottom_axis
        self.hide_top_axis = hide_top_axis

        self.hide_x_ticks = hide_x_ticks
        self.hide_y_ticks = hide_y_ticks
        self.hide_z_ticks = hide_z_ticks

        self.x_label = x_label
        self.y_label = y_label
        self.z_label = z_label

        self.tick_size = tick_size
        self.title_size = title_size
        self.label_size = label_size
        self.group_id_size = group_id_size

        self.show_group_id = show_group_id
        self.show_grid = show_grid

        self.figure_size_x = figure_size_x
        self.figure_size_y = figure_size_y

        self.hide_version_tag = hide_version_tag

        self.clustalo_bin = clustalo_bin
        self.fa_output_dir = fa_output_dir
        self.uid = uid


        if sequence_type == 'auto':
            self.sequence_type = detect_seq_type(self.seqs)
        else:
            self.sequence_type = sequence_type


        self.logos = []

        self.prep_env()

        self.prepare_bits()

        if ax is None:
            self.generate_ax(threed=(self.logo_type=='Threed'))
        else:
            self.ax = ax
        self.generate_components()
    
    def prep_env(self):

        print('in prep env')

        if self.clustalo_bin == '':
            cur_path = pathlib.Path().resolve()
            os.makedirs(f'{cur_path}/bins',exist_ok = True)
            self.clustalo_bin = f'{cur_path}/bins/clustalo'
            if not os.path.exists(f'{cur_path}/bins/clustalo'):
                #determine os
                import platform
                import struct
                platform = platform.system()
                url = ''
                if platform == 'Linux':
                    is_64bit = struct.calcsize('P') * 8 == 64
                    if is_64bit:
                        url = 'wget http://www.clustal.org/omega/clustalo-1.2.4-Ubuntu-x86_64'
                    else:
                        url = 'http://www.clustal.org/omega/clustalo-1.2.4-Ubuntu-32-bit'
                elif platform == 'Darwin':
                    url = 'http://www.clustal.org/omega/clustal-omega-1.2.3-macosx'
            
                os.system(f'wget {url} -O {cur_path}/bins/clustalo')
                os.system(f'chmod u+x {cur_path}/bins/clustalo')
        
        print('self clustalo_bin:', self.clustalo_bin)
        print('self clustalo_bin:', self.clustalo_bin)
        print('self clustalo_bin:', self.clustalo_bin)
        print('self clustalo_bin:', self.clustalo_bin)


    
    def prepare_bits(self):
        
        self.groups = grouping(self.seqs,seq_file=self.seq_file,group_by=self.group_strategy,
                               group_resolution=self.group_resolution,clustalo_bin=self.clustalo_bin,
                               uid=self.uid,fa_output_dir=self.fa_output_dir)
        check_group(self.groups)

        self.probs = compute_prob(self.groups,threshold=self.omit_prob)

        if self.height_algorithm == 'probabilities':
            self.seq_bits = self.probs
        elif self.height_algorithm == 'bits':
            self.seq_bits = compute_bits(self.groups, self.probs, seq_type=self.sequence_type)


        try:
            if self.group_order.lower() == 'length':
                self.group_ids = sorted(self.seq_bits.keys(),key=lambda d: len(self.seq_bits[d]))
            elif self.group_order.lower() == 'length_reverse':
                self.group_ids = sorted(self.seq_bits.keys(),key=lambda d: len(self.seq_bits[d]),reverse=True)
            elif self.group_order.lower() == 'identifier':
                self.group_ids = sorted(self.seq_bits.keys(),key=lambda d: re.split('[@-]',d)[0])
            elif self.group_order.lower() == 'identifier_reverse':
                self.group_ids = sorted(self.seq_bits.keys(),key=lambda d: re.split('[@-]',d)[0], reverse=True)
        except Exception as e:
            print(e)
            self.group_ids = sorted(self.seq_bits.keys())
        
        if self.height_algorithm == 'bits':
            to_del_ids = []
            for gid in self.group_ids:
                total = sum([sum([x[1] for x in col]) for col in self.seq_bits[gid]])
                if total == 0:
                    to_del_ids.append(gid)

            for gid in to_del_ids: 
                self.group_ids.remove(gid)
                del self.probs[gid]
                del self.seq_bits[gid]

        if self.align and self.padding_align:

            if len(self.group_ids) > 1:
                if self.align_metric in ['js_divergence','entropy_bhattacharyya']:
                    probs_list = [self.probs[gid] for gid in self.group_ids]
                    self.scores_mat = get_score_mat(probs_list,align_metric=self.align_metric,gap_score=self.gap_score,seq_type=self.sequence_type)
                    new_probs_list = msa(probs_list,self.scores_mat,align_metric=self.align_metric,gap_score=self.gap_score,seq_type=self.sequence_type)
                    self.probs = dict(zip(self.group_ids, new_probs_list))
                else:
                    seq_bits_list = [self.seq_bits[gid] for gid in self.group_ids]
                    self.scores_mat = get_score_mat(seq_bits_list,align_metric=self.align_metric,gap_score=self.gap_score,seq_type=self.sequence_type)
                    new_seq_bits_list = msa(seq_bits_list,self.scores_mat,align_metric=self.align_metric,gap_score=self.gap_score,seq_type=self.sequence_type)
                    self.seq_bits = dict(zip(self.group_ids, new_seq_bits_list))
            
                self.align_probs_bits()
        
        if self.padding_align:
            if self.display_range_left == 0 or self.display_range_right == -1:
                pass

            self.task_name = f"MetaLogo (Display range: {self.display_range_left} to {self.display_range_right})"

            new_probs = {}
            new_bits = {}

            for gid in self.group_ids:
                new_probs[gid] = self.probs[gid][self.display_range_left: self.display_range_right + 1*(self.display_range_right!=-1)]
                new_bits[gid] = self.seq_bits[gid][self.display_range_left: self.display_range_right + 1*(self.display_range_right!=-1)]
            
            self.full_probs = self.probs.copy()
            self.full_seq_bits = self.seq_bits.copy()
            
            self.probs = new_probs
            self.seq_bits = new_bits
    
    def align_probs_bits(self):
        new_probs = {}
        new_bits = {}
        for gid in self.group_ids:
            new_probs[gid] = []
            new_bits[gid] = []
            prob_i = 0
            bit_i = 0
            while prob_i < len(self.probs[gid]) and bit_i < len(self.seq_bits[gid]):
                if self.probs[gid][prob_i] == []:
                    new_probs[gid].append([])
                    new_bits[gid].append([])
                    prob_i += 1
                elif self.seq_bits[gid][bit_i] == []:
                    new_probs[gid].append([])
                    new_bits[gid].append([])
                    bit_i += 1
                else:
                    new_probs[gid].append(self.probs[gid][prob_i].copy())
                    new_bits[gid].append(self.seq_bits[gid][bit_i].copy())
                    bit_i += 1
                    prob_i += 1

            max_len = max(len(self.probs[gid]),len(self.seq_bits[gid]))
            
            for i in range(len(new_probs[gid]),max_len):
                new_probs[gid].append([])
            for j in range(len(new_bits[gid]),max_len):
                new_bits[gid].append([])

        self.probs = new_probs
        self.seq_bits = new_bits


    def generate_components(self):


        self.help_color_palette = sns.color_palette("hls", len(self.seq_bits))

        self.limited_char_width = self.get_limited_char_width()
        self.generate_all_path()

        for index,group_id in enumerate(self.group_ids):
            bits = self.seq_bits[group_id]
            logo = Logo(bits,ax=self.ax,logo_type=self.logo_type,parent_start=self.start_pos,
                        origin=self.start_pos,id=group_id,
                        help_color=self.help_color_palette[index], color=self.color,
                        column_margin_ratio=self.column_margin_ratio, char_margin_ratio=self.char_margin_ratio,
                        limited_char_width=self.limited_char_width, path_dict=self.path_dict)
            self.logos.append(logo)

    def generate_all_path(self):
        path_dict = {}
        for base in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            tmp_path = TextPath((0,0), base, size=1)
            bbox = tmp_path.get_extents()
            path_dict[base] = [tmp_path, bbox]
        self.path_dict = path_dict

    def set_font(self):
        pass
    
    def draw(self):
        self.compute_positions()

        z_height_3d = max([logo.get_height() for logo in self.logos]+[0])
        for index,logo in enumerate(self.logos):
            logo.draw()
            logo.draw_help(draw_arrow=index==0,z_height_3d=z_height_3d, show_id=self.show_group_id,
                            group_id_size=self.group_id_size)
        
        #draw connect


        if self.align:
            self.draw_connect()


        self.draw_help()
        self.compute_xy()
        self.set_figsize()
        self.ax.set_title(self.task_name,fontsize=self.title_size)

        self.ax.tick_params(labelsize=self.tick_size)


        self.ax.spines['left'].set_visible(not self.hide_left_axis)
        self.ax.spines['right'].set_visible(not self.hide_right_axis)
        self.ax.spines['top'].set_visible(not self.hide_top_axis)
        self.ax.spines['bottom'].set_visible(not self.hide_bottom_axis)


        if  self.hide_x_ticks:
            if self.show_grid:
                self.ax.set_xticklabels([])
            else:
                self.ax.set_xticks([])

        if  self.hide_y_ticks:
            if self.show_grid:
                self.ax.set_yticklabels([])
            else:
                self.ax.set_yticks([])
        if self.hide_z_ticks and self.logo_type == 'Threed':
            if self.show_grid:
                self.ax.set_zticklabels([])
            else:
                self.ax.set_zticks([])
        
        if self.show_grid:
            self.ax.grid(True)
        
        self.ax.set_xlabel(self.x_label,fontsize=self.label_size) 
        self.ax.set_ylabel(self.y_label,fontsize=self.label_size) 

        if self.logo_type == 'Threed':
            self.ax.set_zlabel(self.z_label,fontsize=self.label_size)
        
        if not self.hide_version_tag:
            if self.logo_type == 'Threed':
                #self.ax.text2D(1.005, 0, 'Created by MetaLogo')
                self.ax.text2D(1.005, 0, f'Created by MetaLogo (v{__version__})', transform=self.ax.transAxes,
                    horizontalalignment='left',
                    verticalalignment='bottom',
                    rotation='vertical',
                    color='#6c757d')

            else:
                self.ax.text(1.005, 0, f'Created by MetaLogo (v{__version__})',
                    horizontalalignment='left',
                    verticalalignment='bottom',
                    rotation='vertical',
                    transform=self.ax.transAxes,
                    color='#6c757d')
        

        
    def draw_help(self):
        if self.logo_type == 'Radiation':
            self.draw_radiation_help()
        
        if self.logo_type == 'Circle':
            self.draw_circle_help()
        
        if self.logo_type == 'Horizontal':
            self.draw_hz_help()
    
    def draw_connect(self):
        if self.align_metric in ['js_divergence','entropy_bhattacharyya']:
            self.connected = get_connect([self.probs[gid] for gid in self.group_ids], self.align_metric, 
                                       gap_score=self.gap_score,msa_input=self.padding_align,seq_type=self.sequence_type)
        else:
            self.connected = get_connect([self.seq_bits[gid] for gid in self.group_ids], self.align_metric, 
                                       gap_score=self.gap_score,msa_input=self.padding_align,seq_type=self.sequence_type)
        if self.connect_threshold < 0:
            vals = []
            for group_id in self.connected:
                for pos,arr in self.connected[group_id].items():
                    vals.append(arr[0])
            filtered_sorted_vals = sorted(vals, reverse=True)[:int(len(vals)*abs(self.connect_threshold))]
            if len(filtered_sorted_vals) > 0:
                self.connect_threshold = filtered_sorted_vals[-1]
            else:
                self.connect_threshold = 1E9

        i = -1
        for group_id  in self.group_ids:
            i += 1
            if group_id == self.group_ids[-1]:
                continue
            link = self.connected[i]
            for pos1, arr in link.items():
                r, targets = arr
                if r > self.connect_threshold:
                    for pos2 in targets:
                        self.link_columns(self.logos[i].columns[pos1], self.logos[i+1].columns[pos2])


    
    def link_columns(self, column1, column2, ):

        nodes1 = column1.get_edge()
        nodes2 = column2.get_edge()

        if self.logo_type == 'Threed':
            link_edges((nodes1[0],nodes1[1]), (nodes2[0],nodes2[1]) , self.ax, threed=True, x=0,y=2,z=1, 
                        color=self.align_color, alpha=self.align_alpha)
        else:
            if self.logo_type == 'Radiation':
                link_edges((nodes1[0],nodes1[1]), (nodes2[3],nodes2[2]) , self.ax,
                            color=self.align_color, alpha=self.align_alpha)
            else:
                link_edges((nodes1[3],nodes1[2]), (nodes2[0],nodes2[1]) , self.ax,
                            color=self.align_color, alpha=self.align_alpha)
            link_edges((nodes2[0],nodes2[1]), (nodes2[3],nodes2[2]) , self.ax,
                        color=self.align_color, alpha=self.align_alpha)
            link_edges((nodes1[0],nodes1[1]), (nodes1[3],nodes1[2]) , self.ax,
                        color=self.align_color, alpha=self.align_alpha)


    def draw_circle_help(self):           
        #https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
        if self.show_group_id:
            legend_elements = []
            for logo in self.logos[::-1]:
                legend_elements.append( Line2D([0], [0], marker='o', color=logo.help_color, label=f'{logo.id}', linestyle = 'None', 
                                        markersize=5) )
            self.legend = self.ax.legend(handles=legend_elements,fontsize=self.group_id_size,
                            loc='upper right')
                            #, borderaxespad=0)
                            #,bbox_to_anchor=(1,1))
                            #,columnspacing=0,handletextpad=0,labelspacing=0,borderpad=0)
                            #bbox_transform=self.ax.get_figure().transFigure)
                            #bbox_to_anchor=(1, 1),
                            #bbox_transform=self.ax.get_figure().transFigure)
                            #loc='upper left',bbox_to_anchor=(1.005,1),borderaxespad=0.)
                            #plt.legend(bbox_to_anchor=(1, 1),
                            #bbox_transform=plt.gcf().transFigure)


    def draw_radiation_help(self):
        self.ax.add_patch(Circle(self.start_pos,self.radiation_radius,linewidth=1,fill=False,edgecolor='grey',alpha=0.5))
    
    def draw_hz_help(self):

        if not self.hide_x_ticks:
            maxlen = max([len(bits) for bits in self.seq_bits.values()])
            margin_ratio = 0
            if len(self.logos)>0:
                margin_ratio = self.logos[0].column_margin_ratio

            #self.ax.set_xticks([x+0.5+x*margin_ratio for x in range(maxlen)])
            self.ax.set_xticks([x+x*margin_ratio for x in range(maxlen+1)])
            self.ax.set_xticklabels([str(x) for x in range(maxlen+1)])
        
        if not self.hide_y_ticks:
            total_height = self.ceiling_pos[1]
            ticks = []
            ticklabels = []
            i = -1
            for logo in self.logos:
                i += 1
                start = logo.start_pos[1]
                height = logo.get_height()
                if i==0:
                    ticks.append(0)
                    ticklabels.append(0)
                ticks.append(start+height*(1+self.logo_margin_ratio))
                if i == len(self.logos) - 1:
                    ticklabels.append('%s'%round(height,2))
                else:
                    ticklabels.append('%s/0'%round(height,2))
        
            self.ax.set_yticks(ticks)
            self.ax.set_yticklabels(ticklabels)



    def compute_positions(self):

        if self.logo_type == 'Radiation':
            self.start_pos = (0,0)
            self.radiation_radius = 1
            self.radiation_width = 1
            self.radiation_ratio = 0.9
            thetas = []
            head_ranges = [] 
            for group_id in self.group_ids:
                bit = self.seq_bits[group_id]
                head_range = max([sum([x[1] for x in col])*1.1  for col in bit][:self.radiation_head_n] + [0])
                head_ranges.append(head_range)
            self.radiation_radius = 2 * sum(head_ranges) / (np.pi*self.radiation_ratio)

            thetas = []
            for head_range in head_ranges:
                thetas.append(2*np.arctan(head_range/(2*self.radiation_radius)))

            deg_pointer = (np.pi/2 - sum(thetas))/2
            for index,theta in enumerate(thetas):
                c_deg = np.pi/2 - deg_pointer - theta/2
                deg_pointer += theta
                #start_pos = get_coor_by_angle(self.radiation_radius, c_deg, self.start_pos)
                logo = self.logos[index]
                logo.set_parent_start(self.start_pos)
                logo.set_start_pos((self.radiation_radius,0))
                logo.set_deg(c_deg)
                logo.set_radiation_space(head_ranges[index])
                logo.compute_positions()
        else:
            start_pos = self.start_pos
            if self.logo_type == 'Circle':
                start_pos = (self.start_pos[0], self.start_pos[1]+self.init_radius)
            elif self.logo_type == 'Threed':
                start_pos = (self.start_pos[0], self.start_pos[1], 0)
                self.start_pos = start_pos
            for index,logo in enumerate(self.logos):
                logo.set_parent_start(self.start_pos)
                logo.set_start_pos(start_pos)
                logo.compute_positions()
                if self.logo_type == 'Threed':
                    #start_pos = (start_pos[0], start_pos[1], start_pos[2] + self.threed_interval)
                    start_pos = (start_pos[0], start_pos[1], start_pos[2] + logo.get_height())
                else:
                    start_pos = (start_pos[0], start_pos[1] + logo.get_height()*(1+self.logo_margin_ratio))
            self.ceiling_pos = start_pos
    
    def get_height(self):
        return self.ceiling_pos[1] - self.start_pos[1]
    
    def get_max_logo_height(self):
        return max([logo.get_height() for logo in self.logos]+[0])

    def get_width(self):
        return max([logo.get_width() for logo in self.logos]+[0])

    def compute_xy(self):
        if self.logo_type == 'Horizontal':
            self.ax.set_xlim(self.start_pos[0]-1,self.start_pos[0] + self.get_width()+1)
            self.ax.set_ylim(self.start_pos[1],self.ceiling_pos[1])

            if self.show_group_id:
                r = self.ax.get_figure().canvas.get_renderer()
                x_range = 0
                for i in range(len(self.logos)):
                    text_width = self.logos[i].id_txt.get_window_extent(r).transformed(self.ax.transData.inverted()).width
                    logo_width = self.logos[i].get_width()
                    _range = text_width + 1 + logo_width
                    if _range > x_range:
                        x_range = _range
            
                self.ax.set_xlim(self.start_pos[0],x_range)


        elif self.logo_type == 'Circle':
            radius = self.ceiling_pos[1] - self.start_pos[1]
            if self.show_group_id:
                l = self.legend
                r = self.ax.get_figure().canvas.get_renderer()
                bbox = l.get_window_extent(r)
                bbox2 = bbox.transformed(self.ax.transAxes.inverted())
                padded = 2*radius/(1-bbox2.width) - 2*radius
                self.ax.set_xlim(self.start_pos[0] - radius,self.start_pos[0] + radius + padded)
                self.ax.set_ylim(self.start_pos[1] - radius,self.start_pos[1] + radius + padded)
            else:
                self.ax.set_xlim(self.start_pos[0] - radius,self.start_pos[0] + radius)
                self.ax.set_ylim(self.start_pos[1] - radius,self.start_pos[1] + radius)


        elif self.logo_type == 'Radiation':
            ###
            lims = []
            for logo in self.logos:
                width = logo.get_width()
                lim = max(width*np.sin(logo.deg), width*np.cos(logo.deg))
                lims.append(lim)
            self.ax.set_xlim(self.start_pos[0], self.start_pos[0] + self.radiation_radius + max(lims+[0]))
            self.ax.set_ylim(self.start_pos[1], self.start_pos[1] + self.radiation_radius + max(lims+[0]))

            if self.show_group_id:
                r = self.ax.get_figure().canvas.get_renderer()
                x_range = 0
                for i,logo in enumerate(self.logos):
                    lim = lims[i]
                    text_width = self.logos[i].id_txt.get_window_extent(r).transformed(self.ax.transData.inverted()).width
                    text_lim = max(text_width*np.sin(logo.deg), text_width*np.cos(logo.deg))
                    _range = text_width + text_lim + lim
                    if _range > x_range:
                        x_range = _range

                self.ax.set_xlim(self.start_pos[0], self.start_pos[0] + self.radiation_radius + x_range)
                self.ax.set_ylim(self.start_pos[0], self.start_pos[0] + self.radiation_radius + x_range)

        elif self.logo_type == 'Threed':
            self.ax.set_xlim(self.start_pos[0], self.start_pos[0] + self.get_width())
            self.ax.set_ylim(self.start_pos[1], self.start_pos[1] + sum([logo.get_height() for logo in self.logos[:-1]]) )
            self.ax.set_zlim(self.start_pos[1], self.start_pos[1] + sum([logo.get_height() for logo in self.logos]) )

    
    def set_figsize(self):
        if self.figure_size_x != -1 and self.figure_size_y != -1:
            self.ax.get_figure().set_figwidth(self.figure_size_x)
            self.ax.get_figure().set_figheight(self.figure_size_y)
        else:
            if self.logo_type == 'Circle':
                self.ax.get_figure().set_figheight(10)
                self.ax.get_figure().set_figwidth(10)
            if self.logo_type == 'Horizontal':
                self.ax.get_figure().set_figheight(6)
                self.ax.get_figure().set_figwidth(12)
    

    def get_entropy(self):
        ents = []
        #for grpid,probs in self.probs.items():

        seq_probs = self.probs
        if hasattr(self, 'full_probs'):
            seq_probs = self.full_probs
        
        for grpid in self.group_ids:
            probs = seq_probs[grpid]
            _ents = []
            _i = 0
            for pos in probs:
                _i += 1
                if len(pos) == 0:
                    _ents.append('-')
                    continue
                _ep = [x[1] for x in pos if x[1]>0]
                entropy = -sum([x*np.log(x) for x in _ep ])
                _ents.append(entropy)
            if len(_ents) > 0:
                ents.append(_ents)
        
        return ents


    def get_group_mean_entropy_figure(self):

        fig,ax = plt.subplots()
        ents = self.get_entropy()
        mean_ents = [np.median([y for y in x if y!='-']) for x in ents]
        df = pd.DataFrame(mean_ents)
        df.index = self.group_ids
        df.columns = ['Mean Entropy of Positions']
        ax = df.plot.bar(ax=ax)
        ax.set_xlabel('Group')
        ax.set_ylabel('Mean Entropy of Positions')
        return ax
    
    def get_boxplot_entropy_figure(self):
        fig,ax = plt.subplots()
        ents = self.get_entropy()
        ents = [[y for y in x if y!='-'] for x in ents]
        lists = []
        for i in range(len(ents)):
            grp_id = self.group_ids[i]
            for item in ents[i]:
                lists.append([grp_id,item])
        df = pd.DataFrame(lists,columns=['Group','Entropy of Each Position'])
        return sns.boxplot(data=df,y='Group',x='Entropy of Each Position',ax=ax,order=self.group_ids)



    def get_entropy_figure(self):

        ents = self.get_entropy()


        ent_df = pd.DataFrame(ents)
        ent_df = ent_df.replace('-',0)
        ent_df = ent_df.fillna(0)

        fig,ax = plt.subplots()
        im = ax.imshow(ent_df)
        cbar = ax.figure.colorbar(im, ax=ax,orientation='horizontal')
        cbar.ax.set_xlabel('Entropy')

        kw = dict(horizontalalignment="center",
              verticalalignment="center",color='white')

        for i in range(len(ent_df)):
            for j in range(ent_df.columns.size):
                if j > len(ents[i]) - 1:
                    im.axes.text(j,i,'X',**kw)
                else:
                    if ents[i][j] == '-':
                        im.axes.text(j,i,'X',**kw)
                #else:
                #    im.axes.text(j,i,round(ents[i][j],2),**kw)


        ax.set_xticks(np.arange(ent_df.columns.size))
        ax.set_yticks(np.arange(len(self.group_ids)))
        ax.set_yticklabels(self.group_ids)
        ax.set_xticklabels(np.arange(ent_df.columns.size))
        ax.set_xlabel('Position')
        ax.set_ylabel('Group')
        ax.set_title('Entropy Heatmap')
        fig.tight_layout()

        ##extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

        return fig
    

    def get_correlation_figure(self):

        fig,ax = plt.subplots()

        if not self.padding_align:
            return None
        if len(self.group_ids) < 2:
            return None

        seq_bits = self.seq_bits        
        if hasattr(self, 'full_seq_bits'):
            seq_bits = self.full_seq_bits
        
        aligned_len =  len(seq_bits[self.group_ids[0]])
        if aligned_len < 1:
            return None
        
        bases = []
        for i in range(aligned_len):
            _bases = []
            for grp_id in self.group_ids:
                _bases += [x[0] for x in seq_bits[grp_id][i]]
            bases.append(sorted(list(set(_bases))))

        arrs = []
        for grp_id in self.group_ids:
            bits = seq_bits[grp_id]
            _arr = []
            for i in range(len(bits)):
                _dict = dict(bits[i])
                for base in bases[i]:
                    _arr.append(_dict.get(base,0))
            arrs.append(_arr)
        
        
        try:
            df = pd.DataFrame(arrs)
            df.index = self.group_ids
            df = df.T
            g = sns.clustermap(df.corr(method='pearson'))
            g.ax_heatmap.tick_params(axis='both', which='major', labelsize=15)
            return g
        except:
            return None

    
    def get_grp_counts_figure(self):
        fig,ax = plt.subplots()
        lens = []
        for grp in self.group_ids:
            lens.append([grp,len(self.groups[grp])])
        df = pd.DataFrame(lens,columns=['Group','Counts'])
        ax = df.set_index('Group').plot.bar(ax=ax,y='Counts')
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x() + p.get_width()/2 , p.get_height() * 1.005),ha='center')
        ax.set_title('Sequence counts of each group')

        return ax