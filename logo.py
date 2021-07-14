#!/usr/bin/python
import genericpath
from character import Character
from column import Column

class Logo():
    def __init__(self, bits, h_margin=0.1):
        self.bits = bits
        self.h_margin = h_margin
        self.columns = []
    
    def generate_components(self):
        assert len({len(seq) for seq in self.seqs}) == 1 , 'seqs in one group have different lengths'
        for bit in self.bits:
            chars = [x[0] for x in bit]
            weights = [x[1] for x in bit]
            column = Column(chars,weights)
            self.columns.append(column)



class LogoGroup():
    def __init__(self,  seq_bits, group_order):
        self.seq_bits = seq_bits
        self.group_order = group_order
        self.logos = []
        self.generate_components()

    
    def generate_components(self):
        print('come in generate_components')
        for group_id,bits in self.seq_bits.items():
            logo = Logo(bits)
            self.logos.append(logo)
    
    def set_font(self):
        pass

    def savefig(self):
        pass

        

