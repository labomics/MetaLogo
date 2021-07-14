#!/usr/bin/python
import genericpath
from character import Character
from column import Column
from item import Item


class Logo(Item):
    def __init__(self, bits, ax = None, h_margin=0.1, *args, **kwargs):
        super(Logo, self).__init__(*args, **kwargs)

        self.bits = bits
        self.h_margin = h_margin
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
        for col in self.columns:
            col.draw()



class LogoGroup(Item):
    def __init__(self,  seq_bits, group_order, *args, **kwargs):
        super(LogoGroup, self).__init__(*args, **kwargs)
        self.seq_bits = seq_bits
        self.group_order = group_order
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
        for logo in self.logos:
            logo.draw()


        

