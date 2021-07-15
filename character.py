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

    def __init__(self, char, ax=None, start_pos=(0,0),  target_size=None, limited_width=None, font = 'Arial', color = 'basic_dna_color', alpha = 1, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self.char = char
        self.start_pos = start_pos
        self.target_size = target_size
        self.alpha = alpha
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

    def set_target_size(self, width, height):
        self.target_size = (width, height)

    def set_font(self, font):
        self.font = font

    def set_alpha(self, alpha):
        self.set_alpha = alpha
    
    def get_path_extents(self):
        return self.path.get_extents()

    def get_patch_extents(self):
        return self.patch.get_extents()
    
    def transform(self):
        width,height = self.target_size
        tmp_path = TextPath((0,0), self.char, size=1)
        bbox = tmp_path.get_extents()
        hoffset = (width - bbox.width * width / max(bbox.width,self.limited_width))/2
        transformation = Affine2D() \
            .translate(tx=-bbox.xmin, ty=-bbox.ymin) \
            .scale(sx=width/max(bbox.width,self.limited_width), sy=height/bbox.height) \
            .translate(tx=self.start_pos[0] + hoffset,ty=self.start_pos[1])
        self.path = transformation.transform_path(tmp_path)
        self.patch = PathPatch(self.path, linewidth=0, 
                                facecolor=self.color_map.get(self.char,self.color_map['other']),                              
                                alpha=self.alpha,
                                edgecolor=self.color_map.get(self.char,self.color_map['other']))

    def draw(self):
        self.transform()
        self.ax.add_patch(self.patch)

    def compute_positions(self):
        pass

    def get_height(self):
        return self.target_size[1]

    def get_width(self):
        return self.target_size[0]
