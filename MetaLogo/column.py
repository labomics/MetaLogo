#!/usr/bin/env python
from .character import Character
from .item import Item
from .utils import rotate
import numpy as np
from matplotlib.patches import PathPatch,Rectangle,Circle,Polygon
from matplotlib.path import Path
from .colors import get_color_scheme

basic_dna_color = get_color_scheme('basic_dna_color')


class Column(Item):

    def __init__(self, bases, weights, ax=None, start_pos=(0,0), logo_type = 'Horizontal', char_margin_ratio=0.05,
                 width=1, parent_start=(0,0), origin=(0,0), color=basic_dna_color, *args, **kwargs):
        super(Column, self).__init__(*args, **kwargs)
        self.bases = bases 
        self.weights = weights 
        self.width = width
        self.char_margin_ratio = char_margin_ratio
        self.start_pos = start_pos
        self.parent_start = parent_start
        self.origin = origin
        self.logo_type = logo_type
        self.color = color
        #self.path_hight, self.init_hight, self.target_height = self.get_heights()
        self.characters = []
        if ax == None:
            self.generate_ax(threed=(self.logo_type=='Threed'))
        else:
            self.ax = ax
        self.generate_components()

    def generate_components(self):
        for base,weight in sorted(zip(self.bases,self.weights),key=lambda d:d[1]):
            character = Character(base,width=self.width,height=weight,ax=self.ax,
                                    logo_type=self.logo_type, parent_start=self.start_pos,
                                    origin=self.origin,color=self.color)
            self.characters.append(character)
    
    def draw(self):
        for character in self.characters:
            character.draw()
        
    def draw_wrap(self):
        p1,p2,p3,p4 = self.get_edge()
        verts = [p1,p2,p3,p4,p1]
        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY
        ]
        self.ax.add_patch(PathPatch(Path(verts, codes)))
    
    def compute_positions(self):
        start_pos = self.start_pos
        for character in self.characters:
            character.set_start_pos(start_pos)
            character.set_parent_start(self.start_pos)

            if self.logo_type == 'Circle':
                character.set_deg(self.deg)
            elif self.logo_type == 'Radiation':
                character.set_deg(self.deg)
                character.set_radiation_space(self.radiation_space)

            character.set_width(self.width)
            character.compute_positions()
            if self.logo_type == 'Threed':
                start_pos = (start_pos[0], start_pos[1] + character.get_height() *(1+self.char_margin_ratio), start_pos[2])
            else:
                start_pos = (start_pos[0], start_pos[1] + character.get_height() * (1+self.char_margin_ratio))
    
    def get_height(self):
        height = sum([char.get_height() * (1+self.char_margin_ratio) for char in self.characters[:-1]]) 
        if len(self.characters) > 0:
            height += self.characters[-1].get_height()
        return height

    def get_width(self):
        return max([char.get_width()  for char in self.characters]+[0])
    
    def get_edge(self):

        h = self.get_height()
        w = self.get_width()

        if self.logo_type in 'Horizontal':
            leftbottom = self.start_pos
            rightbottom = (self.start_pos[0]+w, self.start_pos[1])
            righttop = (self.start_pos[0] + w, self.start_pos[1] + h ) 
            lefttop = (self.start_pos[0],self.start_pos[1] + h)
            return leftbottom,rightbottom,righttop,lefttop

        if self.logo_type in 'Threed':
            leftbottom = self.start_pos
            rightbottom = (self.start_pos[0]+w, self.start_pos[1], self.start_pos[2])
            righttop = (self.start_pos[0] + w, self.start_pos[1] + h, self.start_pos[2]) 
            lefttop = (self.start_pos[0],self.start_pos[1] + h, self.start_pos[2])
            return leftbottom,rightbottom,righttop,lefttop

        if self.logo_type == 'Circle':
            p1 = (self.start_pos[0] - w/2, self.start_pos[1])
            p2 = (self.start_pos[0] + w/2, self.start_pos[1])
            p3 = (self.start_pos[0] + w/2, self.start_pos[1]+h)
            p4 = (self.start_pos[0] - w/2, self.start_pos[1]+h)
            nodes = rotate([p1,p2,p3,p4],origin=self.start_pos, angle=self.deg-np.pi/2)
            return nodes
       
        if self.logo_type == 'Radiation':
            p1 = (self.start_pos[0], self.start_pos[1]-self.radiation_space/2)
            p2 = (self.start_pos[0]+w, self.start_pos[1]-self.radiation_space/2)
            p3 = (self.start_pos[0]+w, self.start_pos[1]+h-self.radiation_space/2)
            p4 = (self.start_pos[0], self.start_pos[1]+h-self.radiation_space/2)
            nodes = rotate([p1,p2,p3,p4],origin=self.origin, angle=self.deg)
            return nodes
        


 



        

