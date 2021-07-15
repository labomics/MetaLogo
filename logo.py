#!/usr/bin/python
import genericpath
from character import Character
from column import Column
from item import Item


class Logo(Item):
    def __init__(self, bits, ax = None, start_pos=(0,0), column_margin=0.1, *args, **kwargs):
        super(Logo, self).__init__(*args, **kwargs)

        self.bits = bits
        self.column_margin = column_margin
        self.columns = []

        if ax == None:
            self.ax = self.generate_ax()
        else:
            self.ax = ax
        
        self.generate_components()


    def generate_components(self):
        assert len({len(seq) for seq in self.bits}) == 1 , 'seqs in one group have different lengths'
        for bit in self.bits:
            chars = [x[0] for x in bit]
            weights = [x[1] for x in bit]
            column = Column(chars,weights,ax=self.ax)
            self.columns.append(column)
    
    def draw(self):
        print('in logo draw')
        self.compute_positions()
        for col in self.columns:
            col.draw()
    
    def compute_positions(self):
        start_pos = self.start_pos
        for col in self.columns:
            col.set_start_pos(start_pos)
            col.compute_positions()
            start_pos = (start_pos[0] + col.get_width() + self.column_margin, start_pos[1])
    
    def get_height(self):
        return max([col.get_height() for col in self.columns])
    
    def get_width(self):
        return sum([col.get_width() + self.column_margin for col in self.columns])




class LogoGroup(Item):
    def __init__(self,  seq_bits, group_order, start_pos = (0,0), logo_margin = 0.1, *args, **kwargs):
        super(LogoGroup, self).__init__(*args, **kwargs)
        self.seq_bits = seq_bits
        self.group_order = group_order
        self.start_pos = start_pos
        self.logo_margin = logo_margin
        self.ceiling_pos = ()
        self.logos = []
        self.generate_ax()
        self.generate_components()
    
    def generate_components(self):
        print('come in generate_components')
        for group_id,bits in self.seq_bits.items():
            logo = Logo(bits,ax=self.ax)
            self.logos.append(logo)
    
    def set_font(self):
        pass
    
    def draw(self):
        print('in logo group draw')
        self.compute_positions(self.start_pos)
        for logo in self.logos:
            logo.draw()
        self.compute_xy()

    def compute_positions(self, start_pos):
        for index,logo in enumerate(self.logos):
            logo.set_start_pos(start_pos)
            logo.compute_positions()
            start_pos = (start_pos[0], start_pos[1] + logo.get_height() + self.logo_margin)
        
        self.ceiling_pos = start_pos
    
    def get_height(self):
        return self.ceiling_pos[1] - self.start_pos[1]

    def get_width(self):
        return max([logo.get_width() for logo in self.logos])

    def compute_xy(self):
        self.ax.set_ylim(self.start_pos[1],self.ceiling_pos[1])
        self.ax.set_xlim(self.start_pos[0],self.start_pos[0] + self.get_width())
