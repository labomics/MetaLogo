#!/usr/bin/env python

from matplotlib import pyplot as plt
from matplotlib.textpath import TextPath

class Item():
    def __init__(self, *args, **kwargs) :
        pass

    def generate_ax(self,threed=False,withtree=False):
        if threed:
            fig, ax = plt.subplots(1, 1,figsize=(10,10),subplot_kw=dict(projection="3d"))
            self.ax = ax    
        elif withtree: 
            fig, (ax1,ax2) = plt.subplots(1, 2,figsize=(10,10),gridspec_kw={'width_ratios': [1, 4]})
            self.ax = ax2
            self.ax0 = ax1
            plt.subplots_adjust(wspace=0)
        else:
            fig, ax = plt.subplots(1, 1,figsize=(10,10))
            self.ax = ax    
    
    def draw(self):
        pass
    
    def savefig(self,filename,bbox_inches='tight'):
        if (hasattr(self,'ax')) and (self.ax is not None):
            self.ax.get_figure().savefig(filename,bbox_inches=bbox_inches)

    def set_start_pos(self,start_pos):
        self.start_pos = start_pos
    
    def set_parent_start(self,parent_start):
        self.parent_start = parent_start 

    def set_deg(self,deg):
        self.deg = deg
    
    def set_width(self,width):
        self.width = width

    def set_radiation_space(self,space):
        self.radiation_space = space

    def get_limited_char_width(self, limited_char='E'):
        tmp_path = TextPath((0, 0), 'E', size=1)
        return tmp_path.get_extents().width
