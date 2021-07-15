#!/usr/bin/python
import genericpath
import numpy as np
from matplotlib.patches import Circle
from character import Character
from column import Column
from item import Item
from utils import get_coor_by_angle


class Logo(Item):
    def __init__(self, bits, ax = None, start_pos=(0,0), logo_type='Horizontal', column_width=1, 
                 column_margin=0.1, parent_start = (0,0), *args, **kwargs):
        super(Logo, self).__init__(*args, **kwargs)

        self.bits = bits
        self.start_pos = start_pos
        self.logo_type = logo_type
        self.parent_start = parent_start
        self.column_margin = column_margin
        self.column_width = column_width
        self.columns = []

        if ax == None:
            self.ax = self.generate_ax()
        else:
            self.ax = ax
        
        self.generate_components()


    def generate_components(self):
        assert len({len(seq) for seq in self.bits}) == 1 , 'seqs in one group have different lengths'

        for index,bit in enumerate(self.bits):
            chars = [x[0] for x in bit]
            weights = [x[1] for x in bit]
            column = Column(chars,weights,ax=self.ax,width=self.column_width,logo_type=self.logo_type)
            self.columns.append(column)
    
    def draw(self):
        print('in logo draw')
        self.compute_positions()
        for col in self.columns:
            col.draw()
        
    def draw_circle_help(self):

          self.ax.add_patch(Circle(self.parent_start,self.radius,linewidth=1,fill=False,edgecolor='grey',alpha=0.5))
          space_deg = self.degs[0] + (self.degs[-1] - self.degs[0])/2
          space_coor = get_coor_by_angle(self.radius + self.get_height(),space_deg)
          self.ax.plot([self.parent_start[0],space_coor[0]],[self.parent_start[1],space_coor[1]])

    
    def compute_positions(self):

        if self.logo_type == 'Circle':
            self.column_margin = 0
            self.radius = np.sqrt((self.start_pos[0]-self.parent_start[0])**2 + (self.start_pos[1]-self.parent_start[1])**2)
            self.each_deg = 2*np.pi / len(self.bits)
            width = 2 * self.radius * np.tan(self.each_deg/2)
            width = width * 0.95
            self.column_width = width
            degs = [x*self.each_deg + np.pi/2  for x in range(len(self.bits))]
            degs = degs[::-1]
            degs = [degs.pop()] + degs
            self.degs = degs
        elif self.logo_type == 'Radiation':
            pass


        start_pos = self.start_pos
        for index,col in enumerate(self.columns):
            col.set_parent_start(self.start_pos)
            if self.logo_type == 'Horizontal':
                col.set_start_pos(start_pos)
                col.compute_positions()
                start_pos = (start_pos[0] + col.get_width() + self.column_margin, start_pos[1])
            elif self.logo_type == 'Circle':
                start_pos = get_coor_by_angle(self.radius, self.degs[index], self.parent_start)
                col.set_start_pos(start_pos)
                col.set_deg(self.degs[index])
                col.set_width(self.column_width)
                col.compute_positions()
            else:
                pass

    
    def get_height(self):
        return max([col.get_height() for col in self.columns])
    
    def get_width(self):
        return sum([col.get_width() + self.column_margin for col in self.columns])




class LogoGroup(Item):
    def __init__(self,  seq_bits, group_order, start_pos = (0,0), logo_type = 'Horizontal', init_radius=1, 
                 logo_margin = 0.01, *args, **kwargs):
        super(LogoGroup, self).__init__(*args, **kwargs)
        self.seq_bits = seq_bits
        self.group_order = group_order
        self.start_pos = start_pos
        self.logo_margin = logo_margin
        self.logo_type = logo_type
        self.init_radius = init_radius
        self.ceiling_pos = ()
        self.logos = []
        self.generate_ax()
        self.generate_components()
    
    def generate_components(self):
        print('come in generate_components')
        if self.group_order == 'length':
            group_ids = sorted(self.seq_bits.keys())
        elif self.group_order == 'length_reverse':
            group_ids = sorted(self.seq_bits.keys(),reverse=True)
        else:
            pass
        for group_id in group_ids:
            bits = self.seq_bits[group_id]
            logo = Logo(bits,ax=self.ax,logo_type=self.logo_type,parent_start=self.start_pos)
            self.logos.append(logo)

    def set_font(self):
        pass
    
    def draw(self):
        self.compute_positions()
        for index,logo in enumerate(self.logos):
            logo.draw()
        
        if self.logo_type == 'Circle':
            logo.draw_circle_help()

        self.compute_xy()
        self.set_figsize()

    def compute_positions(self):
        start_pos = self.start_pos
        if self.logo_type == 'Circle':
            start_pos = (self.start_pos[0], self.start_pos[1]+self.init_radius)
        for index,logo in enumerate(self.logos):
            logo.set_parent_start(self.start_pos)
            logo.set_start_pos(start_pos)
            logo.compute_positions()
            start_pos = (start_pos[0], start_pos[1] + logo.get_height() + self.logo_margin)
        self.ceiling_pos = start_pos
    
    def get_height(self):
        return self.ceiling_pos[1] - self.start_pos[1]

    def get_width(self):
        return max([logo.get_width() for logo in self.logos])

    def compute_xy(self):
        if self.logo_type == 'Horizontal':
            self.ax.set_xlim(self.start_pos[0],self.start_pos[0] + self.get_width())
            self.ax.set_ylim(self.start_pos[1],self.ceiling_pos[1])
        elif self.logo_type == 'Circle':
            radius = self.ceiling_pos[1] - self.start_pos[1]
            self.ax.set_xlim(self.start_pos[0] - radius,self.start_pos[0] + radius)
            self.ax.set_ylim(self.start_pos[1] - radius,self.start_pos[1] + radius)
    
    def set_figsize(self):
        if self.logo_type == 'Circle':
            self.ax.get_figure().set_figheight(10)
            self.ax.get_figure().set_figwidth(10)

