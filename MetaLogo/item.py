#!/usr/bin/env python

from matplotlib import pyplot as plt

class Item():
    def __init__(self, *args, **kwargs) :
        pass

    def generate_ax(self,threed=False):
        if threed:
            fig, ax = plt.subplots(1, 1,figsize=(10,10),subplot_kw=dict(projection="3d"))
        else: 
            fig, ax = plt.subplots(1, 1,figsize=(10,10))
        self.ax = ax    
    
    def draw(self):
        pass
    
    def savefig(self,filename):
        if (hasattr(self,'ax')) and (self.ax is not None):
            self.ax.get_figure().savefig(filename)

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