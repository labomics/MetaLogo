#!/usr/bin/python

from matplotlib import pyplot as plt
from matplotlib import patches
import numpy as np
import math
from matplotlib.transforms import Affine2D, Bbox
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch,Rectangle,Circle,Polygon
from matplotlib.path import Path

from item import Item
from colors import get_color_scheme

class Character(Item):

    def __init__(self, char, ax=None, start_pos=(0,0),  width=1, height=1, limited_width=None, 
                    logo_type='Horizontal', font = 'Arial', color = 'basic_dna_color', alpha = 1, 
                    parent_start=(0,0), deg=np.pi/2, origin=(0,0), *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self.char = char
        self.start_pos = start_pos
        self.width = width 
        self.height =  height
        self.logo_type = logo_type
        self.alpha = alpha
        self.parent_start = parent_start
        self.origin = origin
        self.deg = deg
        self.path = None
        self.patch = None
        self.color_map = get_color_scheme(color)
        if ax == None:
            self.generate_ax()
        else:
            self.ax = ax
        if limited_width == None:
            self.limited_width = self.get_limited_width()
        self.generate_components()
    
    def generate_components(self):
        self.path = TextPath(self.start_pos, self.char, size=1)
    
    def get_limited_width(self, limited_char='E'):
        tmp_path = TextPath((0, 0), 'E', size=1)
        return tmp_path.get_extents().width

    def transform_path(self, transformation):
        return transformation.transform_path(self.path)


    def set_font(self, font):
        self.font = font

    def set_alpha(self, alpha):
        self.set_alpha = alpha
    
    def get_path_extents(self):
        return self.path.get_extents()

    def get_patch_extents(self):
        return self.patch.get_extents()
    
    def transform(self):
        width = self.width
        height = self.height
        tmp_path = TextPath((0,0), self.char, size=1)
        bbox = tmp_path.get_extents()
        if self.logo_type == 'Horizontal':
            hoffset = (width - bbox.width * width / max(bbox.width,self.limited_width))/2
            voffset = 0
        elif self.logo_type == 'Circle':
            hoffset = -1*(bbox.width * width / max(bbox.width,self.limited_width))/2
            voffset = 0
        elif self.logo_type == 'Radiation':
            hoffset = 0 
            voffset = -1 * self.radiation_space/2
        else:
            pass

        transformation = Affine2D() \
            .translate(tx=-bbox.xmin, ty=-bbox.ymin) \
            .scale(sx=width/max(bbox.width,self.limited_width), sy=height/bbox.height) \
            .translate(tx=self.start_pos[0] + hoffset,ty=self.start_pos[1] + voffset)
        

        if self.logo_type == 'Circle':
            transformation = transformation.rotate_around(self.parent_start[0], self.parent_start[1], self.deg-np.pi/2) 
        elif self.logo_type == 'Radiation':
            transformation = transformation.rotate_around(self.origin[0], self.origin[1], self.deg)
            #pass
        
        #print('self.parent_start: ',self.parent_start)
        
        #self.ax.annotate(self.start_pos, self.deg)

        self.path = transformation.transform_path(tmp_path)
        self.patch = PathPatch(self.path, linewidth=0, 
                                facecolor=self.color_map.get(self.char,self.color_map['other']),                              
                                alpha=self.alpha,
                                edgecolor=self.color_map.get(self.char,self.color_map['other']))

    def draw(self):
        self.transform()
        self.ax.add_patch(self.patch)
        #print(self.deg)

    def compute_positions(self):
        pass

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width
