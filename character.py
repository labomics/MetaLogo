#!/usr/bin/python

from matplotlib import pyplot as plt
from matplotlib import patches
import numpy as np
import math
from matplotlib.transforms import Affine2D, Bbox
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch,Rectangle,Circle,Polygon
from matplotlib.path import Path


class Character:

    def __init__(self, char, init_corrdinate, target_corrdinate, init_size=None, target_size=None, font = 'Arial', color = 'r', alpha = 1):
        self.char = char
        self.init_corrdinate = init_corrdinate
        self.target_corrdinate = target_corrdinate
        self.init_size = init_size
        self.target_size = target_size
        self.path = None
        self.patch = None

    def generate_path(self):
        self.path = TextPath(self.init_corrdinate, self.char, size=1)

    def generate_patch(self):
        if self.path:
            self.patch = PathPatch(self.path, alpha=self.alpha, linewidth=0)
    
    def transform_path(self, transformation):
        return transformation.transform_path(self.path)

    def set_init_corrdinate(self, x, y):
        self.init_corrdinate = (x,y)
    
    def set_target_corrdinate(self, x, y):
        self.target_corrdinate = (x,y)

    def set_init_size(self, width, height):
        self.init_size = (width, height)

    def set_target_size(self, width, height):
        self.target_size = (width, height)

    def set_font(self, font):
        self.font = font

    def set_color(self, color):
        self.color = color 
    
    def set_alpha(self, alpha):
        self.set_alpha = alpha
    
    def get_path_extents(self):
        return self.path.get_extents()

    def get_patch_extents(self):
        return self.patch.get_extents()
    
    def transform(self):
        pass


 



